# ---------------------------------------------------------------------
# Copyright (c) 2024 Qualcomm Innovation Center, Inc. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# ---------------------------------------------------------------------
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import qai_hub as hub
from prettytable import PrettyTable
from qai_hub.client import SourceModelType
from tabulate import tabulate

from qai_hub_models.utils.base_model import TargetRuntime
from qai_hub_models.utils.compare import METRICS_FUNCTIONS, generate_comparison_metrics
from qai_hub_models.utils.config_loaders import QAIHMModelPerf
from qai_hub_models.utils.qnn_helpers import is_qnn_hub_model

_INFO_DASH = "-" * 60


def print_inference_metrics(
    inference_job: hub.InferenceJob,
    inference_result: Dict[str, List[np.ndarray]],
    torch_out: List[np.ndarray],
    outputs_to_skip: Optional[List[int]] = None,
    metrics: str = "psnr",
) -> None:
    inference_data = [
        np.concatenate(outputs, axis=0) for outputs in inference_result.values()
    ]
    output_names = list(inference_result.keys())
    df_eval = generate_comparison_metrics(
        torch_out, inference_data, names=output_names, metrics=metrics
    )

    def custom_float_format(x):
        if isinstance(x, float):
            return f"{x:.4g}"
        return x

    formatted_df = df_eval.applymap(custom_float_format)

    print(
        f"\nComparing on-device vs. local-cpu inference for {inference_job.name.title()}."
    )
    print(tabulate(formatted_df, headers="keys", tablefmt="grid"))  # type: ignore
    print()

    # Print explainers for each eval metric
    for m in df_eval.columns.drop("shape"):  # type: ignore
        print(f"- {m}:", METRICS_FUNCTIONS[m][1])

    last_line = f"More details: {inference_job.url}"
    print()
    print(last_line)


def print_profile_metrics_from_job(
    profile_job: hub.ProfileJob,
    profile_data: Dict[str, Any],
):
    compute_unit_counts = Counter(
        [op.get("compute_unit", "UNK") for op in profile_data["execution_detail"]]
    )
    execution_summary = profile_data["execution_summary"]
    inference_time_ms = execution_summary["estimated_inference_time"] / 1000
    peak_memory_bytes = execution_summary["inference_memory_peak_range"]
    print(f"\n{_INFO_DASH}")
    print(f"Performance results on-device for {profile_job.name.title()}.")
    print(_INFO_DASH)

    if profile_job.model.model_type == SourceModelType.TFLITE:
        runtime = TargetRuntime.TFLITE
    elif is_qnn_hub_model(profile_job.model):
        runtime = TargetRuntime.QNN
    else:
        raise NotImplementedError()

    print_profile_metrics(
        QAIHMModelPerf.ModelRuntimePerformanceDetails(
            profile_job.model.name,
            profile_job.device.name,
            profile_job.device.os,
            runtime,
            inference_time_ms,
            peak_memory_bytes,
            compute_unit_counts,
        )
    )
    print(_INFO_DASH)
    last_line = f"More details: {profile_job.url}\n"
    print(last_line)


def print_profile_metrics(
    details: QAIHMModelPerf.ModelRuntimePerformanceDetails,
):
    inf_time = details.inference_time_ms
    peak_memory_mb = f"[{round(details.peak_memory_bytes[0] / 1e6)}, {round(details.peak_memory_bytes[1] / 1e6)}]"
    num_ops = sum(details.compute_unit_counts.values())
    compute_units = [
        f"{unit} ({num_ops} ops)"
        for unit, num_ops in details.compute_unit_counts.items()
    ]

    rows = [
        ["Device", f"{details.device_name} ({details.device_os})"],
        ["Runtime", f"{details.runtime.name}"],
        [
            "Estimated inference time (ms)",
            "<0.1" if inf_time < 0.1 else f"{inf_time:.1f}",
        ],
        ["Estimated peak memory usage (MB)", f"{peak_memory_mb}"],
        ["Total # Ops", f"{num_ops}"],
        ["Compute Unit(s)", " ".join(compute_units)],
    ]
    table = PrettyTable(align="l", header=False, border=False, padding_width=0)
    for row in rows:
        table.add_row([row[0], f": {row[1]}"])
    print(table.get_string())


def print_on_target_demo_cmd(
    compile_job: hub.CompileJob, model_folder: Path, device: str
) -> None:
    """
    Outputs a command that will run a model's demo script via inference job.
    """
    assert compile_job.wait().success
    print("\nRun this model on a hosted device on sample data using:")
    target_model = compile_job.get_target_model()
    assert target_model is not None
    print(
        f"python {model_folder / 'demo.py'} "
        "--on-device "
        f"--hub-model-id {target_model.model_id} "
        f'--device "{device}"\n'
    )
