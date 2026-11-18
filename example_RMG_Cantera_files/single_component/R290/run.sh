#!/bin/sh
    
#SBATCH --time=20-00:00:00
#SBATCH --job-name=R290
#SBATCH --error=rmg.slurm.log
#SBATCH --output=output.slurm.log
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=16Gb
#SBATCH --ntasks=1 
#SBATCH --partition=west


python /home/khalil.nor/Code/RMG-Py/rmg.py input.py

