# ConditionalProbabilityMinimization
Solving complex reliability networks using conditional probability. For a detailed explanation of the working of the algorithm check the report.pdf document.

The input to the program is a graph in the format of a tgf file passed as a command line argument, for example: 

***python main.py graph.tgf***

Required packages:

* matplotlib (Install using pip)
* networkx (Install using pip)
* pygraphviz [(see their github)](https://github.com/pygraphviz/pygraphviz) 

## Usage
Run main.py and pass as arguments:
1. graph file path (required)
2. edge name (optional)

Given only a graph file the program will output the conditional probability tree. If the second parameter is added, we generate the 2 sub-systems that results from
reducing the system based on the specified edge.

![](output1.png)

![](output2.png)

