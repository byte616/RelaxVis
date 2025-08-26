import argparse
import re
import ast

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
        self.OPname = ""
        self.attribtes = {}
        self.TIR = ""

def Debug(g):
    print("Nodes:")
    for node in g.nodes.values():
        print(f"  {node.IRname}: shape={node.shape}, type={node.type}, isTuple={node.isTuple}")
        if isinstance(node, OPNode):
            print(f"    OPname: {node.OPname}")
            print(f"    Attributes: {node.attribtes}")
    
    print("Edges:")
    for edge in g.edges:
        print(f"  {edge.src} -> {edge.dest}: shape={edge.shape}, type={edge.type}")

def IRparser(g, f):
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
                type = [type] # for Tuple case

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
            type = match.group("dtype")
            shape = [shape]
            type = [type]
            g.nodes[name] = DataNode(name, shape, type, True)

            

        # parse op node
        if "with R.dataflow():" in line:
            while True:
                if "R.output" in line:
                    break
                line = f.readline()
                # normal op node
                op1_pattern = re.compile(
                    r'(?P<name>[\w_]+):\s*'
                    r'(?P<type_str>R\..*?)\s*=\s*'
                    r'(?P<op_name>R\.[\w_\.]+)'
                    r'\((?P<args_str>.*)\)'
                )
                m = op1_pattern.search(line)
                if m: 
                    name = m.group("name")
                    type_str = m.group("type_str")
                    OPname = m.group("op_name")
                    args_str = m.group("args_str")

                    # process type_str (isTuple / shape / dtype)
                    isTuple = False
                    if "R.Tuple" in type_str:
                        isTuple = True
                    shape_list = []
                    type_list = []
                    type_pattern = re.compile(r'R.Tensor\(\((?P<shape>\d+(,\s*\d+)*,?)\),\s*dtype="(?P<dtype>[\w\d\.]+)')
                    for type_match in type_pattern.finditer(type_str):
                        shape_str = type_match.group("shape")
                        shape = [int(dim) for dim in shape_str.split(",") if dim.strip().isdigit()]
                        dtype = type_match.group("dtype")
                        shape_list.append(shape)
                        type_list.append(dtype)

                    g.nodes[name] = OPNode(name, shape_list, type_list, isTuple)
                    g.nodes[name].OPname = OPname

                    # process args_str (src nodes)
                    arg_pattern = re.compile(r'(?P<arg>[\w_]+)')
                    for arg_match in arg_pattern.finditer(args_str):
                        arg = arg_match.group("arg")
                        if arg in g.nodes:
                            edge = Edge(arg, name, g.nodes[arg].shape, g.nodes[arg].type)
                            g.edges.append(edge)
                            g.nodes[arg].forwrd_edges.append(name)
                            g.nodes[name].back_edges.append(arg)
                        else:
                            continue # attribute or constant
                    
                    # process attributes (use ast module)
                    expr = ast.parse(f"f({args_str})", mode="eval").body  
                    keyword_args = {kw.arg: ast.unparse(kw.value) for kw in expr.keywords}
                    g.nodes[name].attribtes = keyword_args

                    # process metadata
                    meta_pattern = re.compile(r'metadata\[\"relax.expr.Constant\"\]\[(?P<metaid>\d+)\]')
                    for meta_match in meta_pattern.finditer(args_str):
                        metaid = meta_match.group("metaid")
                        metaname = "metadata_" + metaid
                        shape = None
                        type = "relax.expr.Constant"
                        g.nodes[metaname] = DataNode(metaname, shape, type)
                        edge = Edge(metaname, name, g.nodes[metaname].shape, g.nodes[metaname].type)
                        g.edges.append(edge)
                        g.nodes[metaname].forwrd_edges.append(name)
                        g.nodes[name].back_edges.append(metaname)
                    
                    continue


                # TupleGetItem case
                op1_pattern = re.compile(
                    r'(?P<name>[\w_]+):\s*'
                    r'(?P<type_str>R\..*?)\s*=\s*'
                    r'(?P<node>[\w_]+)\[(?P<node_idx>[\d]+)\]'
                )
                m = op1_pattern.search(line)
                if m:
                    name = m.group("name")
                    type_str = m.group("type_str")
                    node = m.group("node")
                    node_idx = m.group("node_idx")
                    Opname = "TupleGetItem[" + node_idx + "]"

                    # process type_str (isTuple / shape / dtype)
                    isTuple = False
                    if "R.Tuple" in type_str:
                        isTuple = True
                    shape_list = []
                    type_list = []
                    type_pattern = re.compile(r'R.Tensor\(\((?P<shape>\d+(,\s*\d+)*,?)\),\s*dtype="(?P<dtype>[\w\d\.]+)')
                    for type_match in type_pattern.finditer(type_str):
                        shape_str = type_match.group("shape")
                        shape = [int(dim) for dim in shape_str.split(",") if dim.strip().isdigit()]
                        dtype = type_match.group("dtype")
                        shape_list.append(shape)
                        type_list.append(dtype)

                    g.nodes[name] = OPNode(name, shape_list, type_list, isTuple)
                    g.nodes[name].OPname = "TupleGetItem"

                    # process src node
                    if node in g.nodes:
                        edge = Edge(node, name, g.nodes[node].shape, g.nodes[node].type)
                        g.edges.append(edge)
                        g.nodes[node].forwrd_edges.append(name)
                        g.nodes[name].back_edges.append(node)
                    else:
                        exit(1)

                    continue


                op2_pattern = re.compile(
                    r'(?P<name>[\w_]+):\s*'
                    r'(?P<type_str>R\..*?)\s*=\s*'
                    r'\((?P<args_str>.*)\)'
                )
                m = op2_pattern.search(line)
                if m:   
                    name = m.group("name")
                    type_str = m.group("type_str")
                    args_str = m.group("args_str")

                    # process type_str (isTuple / shape / dtype)
                    isTuple = False
                    if "R.Tuple" in type_str:
                        isTuple = True
                    shape_list = []
                    type_list = []
                    type_pattern = re.compile(r'R.Tensor\(\((?P<shape>\d+(,\s*\d+)*,?)\),\s*dtype="(?P<dtype>[\w\d\.]+)')
                    for type_match in type_pattern.finditer(type_str):
                        shape_str = type_match.group("shape")
                        shape = [int(dim) for dim in shape_str.split(",") if dim.strip().isdigit()]
                        dtype = type_match.group("dtype")
                        shape_list.append(shape)
                        type_list.append(dtype)

                    g.nodes[name] = OPNode(name, shape_list, type_list, isTuple)
                    g.nodes[name].OPname = "MakeTuple"

                    # process args_str (src nodes)
                    arg_pattern = re.compile(r'(?P<arg>[\w_]+)')
                    for arg_match in arg_pattern.finditer(args_str):
                        arg = arg_match.group("arg")
                        if arg in g.nodes:
                            edge = Edge(arg, name, g.nodes[arg].shape, g.nodes[arg].type)
                            g.edges.append(edge)
                            g.nodes[arg].forwrd_edges.append(name)
                            g.nodes[name].back_edges.append(arg)
                        else:
                            print(f"Error: Node {arg} not found.")
                            exit(1)
                   
                   
def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description = "Arguments: ")
    parser.add_argument("--filepath", type = str, help = "file path")
    args = parser.parse_args()
    
    # Check file exists or not
    try:
        with open(args.filepath, 'r', encoding='utf-8') as f:
            g = Graph() # create empty graph, record nodes and edges
            IRparser(g, f) # parse file and build graph
            Debug(g) # debug test output

    except FileNotFoundError:
        print(f"File not found: {args.filepath}")


if __name__ == "__main__":
    main()