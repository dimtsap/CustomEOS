import numpy as np
import os
import fire


def read_output(index):
    with open(f'./OutputFiles/TotalEOS_{index}.dat') as f:
        lines = f.readlines()

    index_volume_point = 0

    volume=float(lines[10+index_volume_point].split()[0])
    total_free_energy=float(lines[10+index_volume_point].split()[3])
    total_internal_energy=float(lines[10+index_volume_point].split()[4])
    total_pressure=float(lines[10+index_volume_point].split()[5])
    total_entropy=float(lines[10+index_volume_point].split()[6])
    print(f"volume: {volume}, free_energy: {total_free_energy}, internal_energy: {total_internal_energy}, pressure: {total_pressure}, total_entropy:{total_entropy}")

    return total_pressure