# from pathlib import Path
# import re

# def parse_netlist(filepath):
#     device_nodes = {}

#     with open(filepath, 'r') as f:
#         for line in f:
#             line = line.strip()

#             # Skip comments and directives
#             if not line or line.startswith(('*', '.', ';')):
#                 continue

#             # Tokenize line
#             tokens = re.split(r'\s+', line)

#             if not tokens:
#                 continue

#             # Device name (e.g., R4, D4, Q1, XU2)
#             name = tokens[0]

#             # Node names follow the device name
#             nodes = []
#             for token in tokens[1:]:
#                 # Stop if token looks like a value or param (e.g., 10k, V=25)
#                 if re.match(r'^[a-zA-Z_]*=|^[\d.]+[kmunp]?$', token):
#                     break
#                 nodes.append(token)

#             # Save the first 2 nodes (or more if needed)
#             device_nodes[name] = tuple(nodes)

#     return device_nodes


# # === Example Usage ===
# netlist_path = Path(r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_CENTER_NETLIST.txt")
# device_to_nodes = parse_netlist(netlist_path)

# # Pretty print
# for device, nodes in device_to_nodes.items():
#     print(f"{device}: {nodes}")



from pathlib import Path

# def is_component_line(line):
#     # Ignore lines that are not actual component definitions
#     skip_keywords = ['.model', '.lib', '.tran', '.TEMP', '.end', '.backanno']
#     if not line or line.startswith(('*', ';')):
#         return False
#     return not any(line.lower().startswith(k.lower()) for k in skip_keywords)

# def parse_netlist(filepath):
#     netlist_path = Path(filepath)
#     components = {}

#     with netlist_path.open() as f:
#         for line in f:
#             line = line.strip()
#             if not is_component_line(line):
#                 continue

#             tokens = line.split()
#             if not tokens:
#                 continue

#             comp_name = tokens[0]
#             nodes = []

#             # Collect nodes until we hit values or parameters
#             for token in tokens[1:]:
#                 if '=' in token or token.upper().startswith('V(') or token.replace('.', '', 1).isdigit():
#                     break
#                 nodes.append(token)

#             # Add '0' if only one node is present
#             if len(nodes) == 1:
#                 nodes.append("0")

#             components[comp_name] = tuple(nodes)

#     return components

# # Example usage
# filepath = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_CENTER_NETLIST.txt"
# components = parse_netlist(filepath)

# # Print result
# for name, nodes in components.items():
#     print(f"{name}: {nodes}")


from pathlib import Path

def is_component_line(line):
    skip_keywords = ['.model', '.lib', '.tran', '.TEMP', '.end', '.backanno']
    if not line or line.startswith(('*', ';')):
        return False
    return not any(line.lower().startswith(k.lower()) for k in skip_keywords)

def parse_netlist(filepath):
    netlist_path = Path(filepath)
    components = {}

    with netlist_path.open() as f:
        for line in f:
            line = line.strip()
            if not is_component_line(line):
                continue

            tokens = line.split()
            if not tokens:
                continue

            comp_name = tokens[0]
            nodes = []

            # Collect only tokens starting with 'N' or '0'
            for token in tokens[1:]:
                if token.upper().startswith('N') or token == '0':
                    nodes.append(token)

            # Ensure at least two nodes for consistency
            if len(nodes) == 1:
                nodes.append("0")

            components[comp_name] = tuple(nodes)

    return components

# Example usage
filepath = r"D:\OneDrive - TVS Motor Company Ltd\Desktop\simdata1\FPL_CENTER_NETLIST.txt"
components = parse_netlist(filepath)

# Print result
for name, nodes in components.items():
    print(f"{name}: {nodes}")
