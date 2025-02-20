# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
import os
from typing import Type

from qai_hub_models.models._shared.cityscapes_segmentation.app import (
    CityscapesSegmentationApp,
)
from qai_hub_models.models._shared.cityscapes_segmentation.model import (
    MODEL_ASSET_VERSION,
    MODEL_ID,
    CityscapesSegmentor,
)
from qai_hub_models.utils.args import (
    demo_model_from_cli_args,
    get_model_cli_parser,
    get_on_device_demo_parser,
    validate_on_device_demo_args,
)
from qai_hub_models.utils.asset_loaders import CachedWebModelAsset, load_image
from qai_hub_models.utils.base_model import TargetRuntime
from qai_hub_models.utils.display import display_or_save_image
from qai_hub_models.utils.image_processing import pil_resize_pad, pil_undo_resize_pad

# This image showcases the Cityscapes classes (but is not from the dataset)
TEST_CITYSCAPES_LIKE_IMAGE_NAME = "cityscapes_like_demo_2048x1024.jpg"
TEST_CITYSCAPES_LIKE_IMAGE_ASSET = CachedWebModelAsset.from_asset_store(
    MODEL_ID, MODEL_ASSET_VERSION, TEST_CITYSCAPES_LIKE_IMAGE_NAME
)


# Run Imagenet Classifier end-to-end on a sample image.
# The demo will print the predicted class to terminal.
def cityscapes_segmentation_demo(
    model_type: Type[CityscapesSegmentor],
    model_id: str,
    is_test: bool = False,
):
    # Demo parameters
    parser = get_model_cli_parser(model_type)
    parser = get_on_device_demo_parser(
        parser, available_target_runtimes=[TargetRuntime.TFLITE], add_output_dir=True
    )
    parser.add_argument(
        "--image",
        type=str,
        help="File path or URL to an input image to use for the demo.",
    )
    args = parser.parse_args([] if is_test else None)
    validate_on_device_demo_args(args, model_type.get_model_id())

    if args.image is None:
        image = TEST_CITYSCAPES_LIKE_IMAGE_ASSET.fetch()
        image_name = TEST_CITYSCAPES_LIKE_IMAGE_NAME
    else:
        image = args.image
        image_name = os.path.basename(image)

    input_spec = model_type.get_input_spec()

    inference_model = demo_model_from_cli_args(model_type, args)
    app = CityscapesSegmentationApp(inference_model)

    (_, _, height, width) = input_spec["image"][0]
    orig_image = load_image(image)
    image, scale, padding = pil_resize_pad(orig_image, (height, width))

    # Run app
    image_annotated = app.predict(image)

    # Resize / unpad annotated image
    image_annotated = pil_undo_resize_pad(
        image_annotated, orig_image.size, scale, padding
    )

    if not is_test:
        display_or_save_image(
            image_annotated,
            args.output_dir,
            "annotated_" + image_name,
            "predicted image",
        )
