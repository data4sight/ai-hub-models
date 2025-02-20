# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from __future__ import annotations

import torch
import torch.nn as nn
from ultralytics import FastSAM

from qai_hub_models.utils.base_model import BaseModel
from qai_hub_models.utils.input_spec import InputSpec


class Fast_SAM(BaseModel):
    """Exportable FastSAM model, end-to-end."""

    def __init__(self, model: nn.Module) -> None:
        super().__init__()
        self.model = model

    @classmethod
    def from_pretrained(cls, ckpt_name: str):
        model = FastSAM(ckpt_name).model
        model.eval()
        return cls(model)

    def forward(self, image: torch.Tensor):
        """
        Run FastSAM on `image`, and produce high quality segmentation masks.
        Faster than SAM as it is based on YOLOv8.

        Parameters:
            image: Pixel values pre-processed for encoder consumption.
                   Range: float[0, 1]
                   3-channel Color Space: BGR
        Returns:

        """
        predictions = self.model(image)
        # Return predictions as a tuple instead of nested tuple.
        return (
            predictions[0],
            predictions[1][0][0],
            predictions[1][0][1],
            predictions[1][0][2],
            predictions[1][1],
            predictions[1][2],
        )

    def get_input_spec(
        self,
        batch_size: int = 1,
        num_channels: int = 3,
        height: int = 640,
        width: int = 640,
    ) -> InputSpec:
        """
        Returns the input specification (name -> (shape, type). This can be
        used to submit profiling job on Qualcomm® AI Hub.
        """
        return {"image": ((batch_size, num_channels, height, width), "float32")}
