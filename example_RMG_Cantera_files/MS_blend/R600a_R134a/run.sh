#!/bin/sh
    
#SBATCH --time=2-00:00:00
#SBATCH --job-name=R600a_R134a
#SBATCH --error=rmg.slurm.log
#SBATCH --output=output.slurm.log
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=32Gb
#SBATCH --ntasks=1 
#SBATCH --exclude=c5003
#SBATCH --partition=short


python /home/khalil.nor/Code/RMG-Py/rmg.py input.py

