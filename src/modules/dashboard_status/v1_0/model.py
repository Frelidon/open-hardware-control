# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate existing canonical inventory summaries, never guess missing values."""
import re

PCI_ADDRESS = re.compile(r"(?:^|[ ·])(?:[0-9a-f]{4}:)?[0-9a-f]{2}:[0-9a-f]{2}\.[0-7](?:$|[ ·])", re.I)
TOPOLOGY = re.compile(r"^(?:(\d+) Kerne · )?(\d+) Threads$")
VRAM = re.compile(r"^(\d+(?:[.,]\d+)?) GiB VRAM$")


def topology_counts(value):
    match = TOPOLOGY.fullmatch(str(value).strip())
    if not match: return None, None
    cores = int(match[1]) if match[1] else None
    threads = int(match[2])
    if threads < 1 or (cores is not None and not 1 <= cores <= threads): return None, None
    return cores, threads


def recognition(cpu_model, cpu_topology, gpu_model, gpu_memory, gpu_path):
    cores, threads = topology_counts(cpu_topology)
    cpu = bool(isinstance(cpu_model, str) and cpu_model.strip() and
               cpu_model.strip() not in {"—", "Prozessor nicht erkannt"})
    gpu = bool(isinstance(gpu_model, str) and gpu_model.strip() and
               gpu_model.strip() not in {"—", "Grafikkarte nicht erkannt"} and
               PCI_ADDRESS.search(str(gpu_path)))
    memory = VRAM.fullmatch(str(gpu_memory).strip())
    return {
        "cpu_model": cpu,
        "cpu_topology": bool(cpu and threads is not None),
        "gpu_model": gpu,
        "gpu_memory": bool(gpu and memory and float(memory[1].replace(",", ".")) > 0),
    }
