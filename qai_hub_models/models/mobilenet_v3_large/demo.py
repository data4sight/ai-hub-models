# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from qai_hub_models.models._shared.imagenet_classifier.demo import imagenet_demo
from qai_hub_models.models.mobilenet_v3_large.model import MobileNetV3Large


def main(is_test: bool = False):
    imagenet_demo(MobileNetV3Large, is_test)


if __name__ == "__main__":
    main()
