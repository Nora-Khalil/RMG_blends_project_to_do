#!/bin/bash
#SBATCH --job-name=fc_R290
#SBATCH --output=fc_all.slurm.log
#SBATCH --error=error_fc_all.slurm.log
##SBATCH --nodes=1
#SBATCH --partition=short
##SBATCH --mem=20Gb
#SBATCH --time=2-00:00:00
#SBATCH --cpus-per-task=8


python flamespeeds.py
