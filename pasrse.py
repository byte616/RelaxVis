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
    def __init__(self, IRname, shape, type):
        self.IRname = IRname
        self.shape = shape  
        self.type = type
        self.forwrd_edges = []
        self.back_edges = []

class OPNode(DataNode):
    def __init__(self, IRname, shape, type):
        super().__init__(IRname, shape, type)
        self.attribtes = {}
        self.TIR = ""

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

                # create DataNode and add to graph
                g.nodes[name] = DataNode(name, shape, type)
                
                # test print
                print(f"DataNode: {g.nodes[name].IRname}, shape: {g.nodes[name].shape}, type: {g.nodes[name].type}")



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