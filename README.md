# Introduction to lineage-entropy
Welcome to the "lineage-entropy" GitHub repository! We are so excited to have you here. This website contains python files that the Garg Lab has used to analyze data in *Lineages of embryonic stem cells show non-Markovian state transition.* We have separated our files based on their functionalities into three different folders in this repository. 

**Please note that the FASTQ files can be found in Sequence Read Archive (SRA) with Bioproject: PRJNA670562.**
 
1. **Fastq_Decomplexation** folder contains python files that are used to parse FASTQ files and collapse barcodes based on their PHRED score and their similarites. 
2. **Data_Analysis** folder contains python files that are used to analyze read counts and generate figures.
3. **Pickle_Files** folder contains binary-serialized pickle files which contains collapsed and normalized barcode data. We used these pickle files in all of our downstream analyses. 

## Getting started 
1. Install python by visiting [official website](https://www.python.org/downloads/). 
2. Install the following dependencies
	- numpy
	- scipy
	- pandas
	- seaborn
	- biopython
	- python-igraph
	- graphviz
	- networkx
	- scipy
	- rpy2
  
  **If you do not use conda environment** type `pip install numpy scipy pandas seaborn biopython python-igraph graphviz networkx scipy rpy2` into your terminal or command prompt.
  
  **For conda environment,** you can use command `conda install numpy scipy pandas seaborn biopython python-igraph graphviz networkx scipy rpy2`.   
  
3. - If you want to analyze FASTQ files, you can navigate to **Fastq_Decomplexation** folder. Instructions for analysis can be found inside. 
   - If you want to work with already decomplexed files, please go to **Pickle_Files** folder and download pickle files there. These pickle files only contain scientific data related to this experiment; they will not harm your computer. 
   
4. Download python files in **Data_Analysis** folder to the same directory that contains the decomplexed FASTQ files (pickle files.)
5. Have fun analyzing data!

If you encounter any problems or have any question, please contact Tee Udomlumleart (teeu@mit.edu). 

Created and maintained by Tee Udomlumleart. Last update 6/18/2021. 
