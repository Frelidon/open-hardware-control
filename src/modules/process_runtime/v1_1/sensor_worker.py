# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only small sensor worker; stdio IPC and no Qt/native USB dependencies."""
import json
from dataclasses import asdict
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from kraken_sensors import SystemMetricSampler, read_amd_cpu_temperature, read_amd_gpu_temperature
from modules.temperature_history.v1_2.sensors import read_linux_temperature_sensors


def sample(sampler):
    cpu, cpu_label = read_amd_cpu_temperature()
    gpu, gpu_label = read_amd_gpu_temperature()
    return dict(schema=1, cpu=cpu, cpu_label=cpu_label, gpu=gpu, gpu_label=gpu_label,
                sensors=[asdict(s) for s in read_linux_temperature_sensors()[:256]],
                metrics=sampler.sample(), sampled_at=time.monotonic())


def run(input_stream, output_stream):
    sampler = SystemMetricSampler()
    for line in iter(lambda: input_stream.readline(4097), ''):
        if len(line) > 4096 or not line.endswith('\n'): return 2
        request = json.loads(line)
        if request == {'op': 'stop'}: return 0
        if request != {'op': 'sample'}: return 2
        output_stream.write(json.dumps(sample(sampler), allow_nan=False) + '\n')
        output_stream.flush()
    return 0


if __name__ == '__main__':
    raise SystemExit(run(sys.stdin, sys.stdout))
