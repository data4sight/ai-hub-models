# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from qai_hub_models.models._shared.imagenet_classifier.demo import imagenet_demo
from qai_hub_models.models.squeezenet1_1_quantized.model import SqueezeNetQuantizable


def main(is_test: bool = False):
    imagenet_demo(SqueezeNetQuantizable, is_test)


if __name__ == "__main__":
    main()
