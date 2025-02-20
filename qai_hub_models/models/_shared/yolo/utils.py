# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from __future__ import annotations

import torch

from qai_hub_models.utils.asset_loaders import CachedWebModelAsset, load_image
from qai_hub_models.utils.base_model import InputsType
from qai_hub_models.utils.image_processing import app_to_net_image_inputs


def transform_box_layout_xywh2xyxy(boxes: torch.Tensor) -> torch.Tensor:
    """
    Convert boxes with (xywh) layout to (xyxy)

    Parameters:
        boxes (torch.Tensor): Input boxes with layout (xywh)

    Returns:
        torch.Tensor: Output box with layout (xyxy)
            i.e. [top_left_x | top_left_y | bot_right_x | bot_right_y]
    """
    # Convert to (x1, y1, x2, y2)
    # TODO(#8595): Splitting ops into smaller chunks makes them NPU resident
    cx = torch.split(boxes[..., 0], 5000, dim=-1)
    cy = torch.split(boxes[..., 1], 5000, dim=-1)
    w_2 = torch.split(boxes[..., 2] / 2, 5000, dim=-1)
    h_2 = torch.split(boxes[..., 3] / 2, 5000, dim=-1)
    boxes_splits = []
    for i in range(len(cx)):
        top_left_x = cx[i] - w_2[i]
        top_left_y = cy[i] - h_2[i]
        bot_right_x = cx[i] + w_2[i]
        bot_right_y = cy[i] + h_2[i]
        boxes = torch.stack((top_left_x, top_left_y, bot_right_x, bot_right_y), -1)
        boxes_splits.append(boxes)
    return torch.cat(boxes_splits, dim=-2)


def detect_postprocess(detector_output: torch.Tensor):
    """
    Post processing to break Yolo(v6,v7) detector output into multiple, consumable tensors (eg. for NMS).
        such as bounding boxes, classes, and confidence.

    Parameters:
        detector_output: torch.Tensor
            The output of Yolo Detection model
            Shape is [batch, num_preds, k]
                where, k = # of classes + 5
                k is structured as follows [boxes (4) : conf (1) : # of classes]
                and boxes are co-ordinates [x_center, y_center, w, h]

    Returns:
        boxes: torch.Tensor
            Bounding box locations. Shape is [batch, num preds, 4] where 4 == (x1, y1, x2, y2)
        scores: torch.Tensor
            class scores multiplied by confidence: Shape is [batch, num_preds]
        class_idx: torch.tensor
            Shape is [batch, num_preds, 1] where the last dim is the index of the most probable class of the prediction.
    """
    # Break output into parts
    boxes = detector_output[:, :, :4]
    conf = detector_output[:, :, 4:5]
    scores = detector_output[:, :, 5:]

    # Convert boxes to (x1, y1, x2, y2)
    boxes = transform_box_layout_xywh2xyxy(boxes)

    # Combine confidence and scores.
    scores *= conf

    # Get class ID of most likely score.
    scores, class_idx = get_most_likely_score(scores)

    return boxes, scores, class_idx


def get_most_likely_score(scores: torch.Tensor):
    """
    Returns most likely score and class id

    Args:
        scores (torch.tensor): final score after post-processing predictions

    Returns:
        scores: torch.Tensor
            class scores reduced to keep max score per prediction
            Shape is [batch, num_preds]
        class_idx: torch.tensor
            Shape is [batch, num_preds] where the last dim is the index of the most probable class of the prediction.
    """
    # TODO(#8595): QNN crashes when running max on a large tensor
    # Split into chunks of size 5k to keep the model NPU resident
    score_splits = torch.split(scores, 5000, dim=-2)
    max_scores = []
    max_indices = []
    for split in score_splits:
        scores, class_idx = torch.max(split, -1, keepdim=False)
        max_scores.append(scores)
        max_indices.append(class_idx.float())
    return torch.cat(max_scores, dim=-1), torch.cat(max_indices, dim=-1)


def yolo_sample_inputs() -> InputsType:
    image_address = CachedWebModelAsset.from_asset_store(
        "yolov7", 1, "yolov7_demo_640.jpg"
    )
    image = load_image(image_address)
    return {"image": [app_to_net_image_inputs(image)[1].numpy()]}
