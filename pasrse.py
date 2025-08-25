import argparse
import re

class Graph:
    def __init__(self):
        self.nodes = {} # node map: {IRname: DataNode / OPNode}
        self.edges = [] # edge list

class Edge:
    def __init__(self, src, dest, shape, type):
        self.src = src # src: IRname of source node
        self.dest = dest # dest: IRname of destination node
        self.shape = shape
        self.type = type

class DataNode:
    def __init__(self, IRname, shape, type, isTuple=False):
        self.IRname = IRname
        self.shape = shape  
        self.type = type
        self.isTuple = isTuple
        self.forwrd_edges = []
        self.back_edges = []

class OPNode(DataNode):
    def __init__(self, IRname, shape, type, isTuple=False):
        super().__init__(IRname, shape, type, isTuple)
        self.attribtes = {}
        self.TIR = ""

def Debug(g):
    print("Nodes:")
    for node in g.nodes.values():
        print(f"  {node.IRname}: shape={node.shape}, type={node.type}, isTuple={node.isTuple}")
    
    # print("Edges:")
    # for edge in g.edges:
    #     print(f"  {edge.src} -> {edge.dest}: shape={edge.shape}, type={edge.type}")

def IRparser(f):
    # node map
    g = Graph()

    # parse file content
    while True:
        line = f.readline()
        # break if EOF
        if not line:
            break
        # parse data node
        if "@R.function" in line:
            line = f.readline()
            
            # match.group(1): all the arguments in main function
            match = re.search(r"def main\((.*)\) ->", line)
            if not match:
                print("Error: No main function found.")
                exit(1)
            
            all_args = match.group(1)
            param_pattern = re.compile(r'(?P<name>[\w_]+):\s*R\.Tensor\(\((?P<shape>\d+(,\s*\d+)*,?)\),\s*dtype="(?P<dtype>[\w\d\.]+)"\)')

            for param_match in param_pattern.finditer(all_args):
                name = param_match.group("name")
                type = param_match.group("dtype")

                # parse shape
                shape_str = param_match.group("shape")
                shape = [int(dim) for dim in shape_str.split(",") if dim.strip().isdigit()]
                shape = [shape] 

                # create DataNode and add to graph
                g.nodes[name] = DataNode(name, shape, type)

            # output node
            match = re.search(r'->\s*R.Tuple\(R.Tensor\(\((?P<shape>\d+(,\s*\d+)*,?)\),\s*dtype="(?P<dtype>[\w\d\.]+)"\)\):', line)
            if not match:
                print("Error: No Output Node.")
                exit(1)
            name = "output"
            shape = [int(dim) for dim in match.group("shape").split(",") if dim.strip().isdigit()]
            shape = [shape]
            type = match.group("dtype")
            g.nodes[name] = DataNode(name, shape, type, True)

            # debug test output
            Debug(g)

        # parse op node
        if "with R.dataflow():" in line:
            while True:
                if "R.output" in line:
                    break
                line = f.readline()
                print(line)


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description = "Arguments: ")
    parser.add_argument("--filepath", type = str, help = "file path")
    args = parser.parse_args()
    
    # Check file exists or not
    try:
        with open(args.filepath, 'r', encoding='utf-8') as f:
            IRparser(f)

    except FileNotFoundError:
        print(f"File not found: {args.filepath}")


if __name__ == "__main__":
    main()