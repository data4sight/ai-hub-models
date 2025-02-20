# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from qai_hub_models.models._shared.ffnet.test_utils import run_test_off_target_numerical
from qai_hub_models.models.ffnet_78s_quantized.demo import main as demo_main
from qai_hub_models.models.ffnet_78s_quantized.model import FFNet78SQuantizable
from qai_hub_models.utils.testing import skip_clone_repo_check


@skip_clone_repo_check
def test_off_target_numerical():
    run_test_off_target_numerical(
        FFNet78SQuantizable,
        "segmentation_ffnet78S_dBBB_mobile",
        relax_numerics=True,
    )


def test_demo():
    demo_main(is_test=True)
