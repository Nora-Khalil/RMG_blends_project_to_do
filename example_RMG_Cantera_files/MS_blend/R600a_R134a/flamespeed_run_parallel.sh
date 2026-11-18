#!/bin/bash
#SBATCH --job-name=fc_R600a_R134a
#SBATCH --output=fc_all.slurm.%a.log
#SBATCH --error=error_fc_all.slurm.%a.log
##SBATCH --nodes=1
#SBATCH --partition=short
##SBATCH --mem=20Gb
#SBATCH --time=2-00:00:00
#SBATCH --cpus-per-task=8
#SBATCH --exclude=c5003
#SBATCH --array=1-60


index=$SLURM_ARRAY_TASK_ID

python flamespeeds_parallel.py $index
