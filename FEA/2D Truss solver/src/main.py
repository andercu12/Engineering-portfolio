"""Educational 2D truss solver, version 1.0.0. Units: N, mm and MPa."""
import numpy as np
import pandas as pd
import re # Check if the format matches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path


def tabulate(rows, headers, tablefmt=None, floatfmt=".6f"):
    """Format result tables using the existing pandas dependency."""
    return pd.DataFrame(rows, columns=headers).to_string(
        index=False, float_format=lambda value: format(value, floatfmt))

Area = 1200.00 # mm2
E = 200.00 # GPa
E_Nmm2 = E * 1000 # N/mm2

# ============================================================
# DESIGN SPACE
# ============================================================

node_min_value = 0 # mm
node_max_value = 100000 # mm

force_min_value = -99999999 # N
force_max_value = 99999999 # N


# ============================================================
# MODEL
# ============================================================

def link_length (x1, y1, x2 , y2):

    return ((x2-x1)**2 + (y2-y1)**2)**(1/2)

def orientation_between_links(coord1, coord2):

    x_2 = coord2[0]
    x_1 = coord1[0]
    y_2 = coord2[1]
    y_1 = coord1[1]

    length = link_length ( x_1, y_1, x_2, y_2)

    if length <= 0:
        raise ValueError("Elements must have a positive length.")

    l = (x_2 - x_1) / length
    m = (y_2 - y_1) / length

    return length, l , m

def stiffness_matrix (l, m , A, E, L):

    transform_matrix = np.array ([
                                [l ** 2  ,  l * m  , -l ** 2 , -l * m],
                                [l * m   ,  m ** 2 , -l * m  , -m ** 2],
                                [-l ** 2 , -l * m  ,  l ** 2 ,  l * m],
                                [-l * m  , -m ** 2 ,  l * m  ,  m ** 2]
                                ])
    
    k_local =  transform_matrix * (A * E / L) 

    return k_local

# ============================================================
# VISUALIZATION
# ============================================================

def initialize_dynamic_plot(max_length):
    
    #Create interactive figure.
    
    plt.ion()

    fig, ax = plt.subplots(figsize=(12, 4.5), constrained_layout=True)

    margin = max_length * 1.5

    ax.set_xlim(-margin, margin)

    ax.set_ylim(-margin, margin)

    ax.set_aspect("equal", adjustable = "box")

    ax.grid(True)

    ax.set_xlabel("X [mm]")

    ax.set_ylabel("Y [mm]")

    ax.set_title("2D Truss")

    line, = ax.plot([], [], marker="o", linewidth = 2)

    return fig, ax, line

def extract_points_array(nodes,pos):

    points = []

    for node in nodes:
        point = node[pos]
        points.append(point)

    return points

def draw_truss(ax, nodes, elements):

    # Draw the complete structure 
    
    ax.clear()
    
    x_points = np.array(extract_points_array(nodes,pos = 0))
    y_points = np.array(extract_points_array(nodes,pos = 1))

    # Store connection directions to help with label placement if needed
    node_direction = {i:[] for i in range (len(nodes))}

    # --------------------------------------------------------
    # Draw elements 
    # --------------------------------------------------------
    
    for element in elements:
    
        node_start = element[0] -1
        node_end = element [1] - 1 
    
        # Coordinates of the connected nodes
        x_coords = [x_points[node_start], x_points[node_end]]
        y_coords = [y_points[node_start], y_points[node_end]]
            
        # Draw the element
        ax.plot(x_coords, y_coords, 'b-', linewidth=3.0, solid_capstyle="round", zorder=1)  

        #Direction vectors for each connected node
        vec = np.array([x_points[node_end] - x_points[node_start], 
                        y_points[node_end] - y_points[node_start]])

        #Normalize to obtain only direction
        mag = np.linalg.norm(vec)
        if mag > 0:
            node_direction[node_start].append(vec / mag)
            node_direction[node_end].append(-vec / mag)

    # --------------------------------------------------------
    # Draw nodes
    # --------------------------------------------------------

    #Draw the nodes
    ax.plot(x_points, y_points, linestyle="none", marker="o", color="blue", markersize=10)

    # --------------------------------------------------------
    # Draw node labels 
    # --------------------------------------------------------

    y_mid = 0.5 * (np.min(y_points) + np.max(y_points))
    
    for number, (x, y) in enumerate(nodes, start=1):
        # Put top-node labels above, bottom-node labels below
        if y > y_mid:
            offset = (0, 10)
            va = "bottom"
        else:
            offset = (0, -12)
            va = "top"
    
        ax.annotate(
            f"N{number}",
            (x, y),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=10,
            weight="bold",
            zorder=3,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=0.6)
        )


    # --------------------------------------------------------
    # Axes formatting
    # --------------------------------------------------------
    x_min, x_max = np.min(x_points), np.max(x_points)
    y_min, y_max = np.min(y_points), np.max(y_points)
    
    x_margin = max((x_max - x_min) * 0.05, 200)
    y_margin = max((y_max - y_min) * 0.15, 200)

    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_title("2D Truss Configuration")
    ax.margins(0)

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

def draw_truss_stresses(ax, nodes, elements, elements_data,fixed_node,mobile_node):
    """
    Draw the truss colored by axial stress sign:
    - Red  : tension
    - Blue : compression
    - Gray : near zero
    """

    ax.clear()

    x_points = np.array(extract_points_array(nodes, pos=0), dtype=float)
    y_points = np.array(extract_points_array(nodes, pos=1), dtype=float)

    # Tolerance to classify near-zero stresses
    tol = 1e-9

    # Store connection directions to help with label placement if needed
    node_direction = {i: [] for i in range(len(nodes))}

    # --------------------------------------------------------
    # Draw elements with only two main colors
    # --------------------------------------------------------
    for idx, (n1, n2) in enumerate(elements):
        node_start = n1 - 1
        node_end = n2 - 1

        x_coords = [x_points[node_start], x_points[node_end]]
        y_coords = [y_points[node_start], y_points[node_end]]

        stress = elements_data[idx]["axial_stress"]

        if stress > tol:
            link_colour = "red"       # Tension
        elif stress < -tol:
            link_colour = "blue"      # Compression
        else:
            link_colour = "gray"      # Zero / Almost zero stress

        ax.plot(
            x_coords, y_coords,
            color=link_colour,
            linewidth=3.0,
            solid_capstyle="round",
            zorder=1
        )

        # Direction vectors for each connected node
        vec = np.array([
            x_points[node_end] - x_points[node_start],
            y_points[node_end] - y_points[node_start]
        ])

        mag = np.linalg.norm(vec)
        if mag > 0:
            node_direction[node_start].append(vec / mag)
            node_direction[node_end].append(-vec / mag)

        mid_x = 0.5 * (x_points[node_start] + x_points[node_end])
        mid_y = 0.5 * (y_points[node_start] + y_points[node_end])

        ax.annotate(
            f"{stress:.2f}",
            (mid_x, mid_y),
            xytext=(0, 0),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=8,
            bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=0.4)
        )

    # --------------------------------------------------------
    # Draw nodes
    # --------------------------------------------------------
    ax.plot(
        x_points, y_points,
        linestyle="none",
        marker="o",
        color="black",
        markersize=8,
        zorder=2
    )

    # --------------------------------------------------------
    # Draw node labels 
    # --------------------------------------------------------
    y_mid = 0.5 * (np.min(y_points) + np.max(y_points))

    for number, (x, y) in enumerate(nodes, start=1):
        # Put top-node labels above, bottom-node labels below
        if y > y_mid:
            offset = (0, 10)
            va = "bottom"
        else:
            offset = (0, -12)
            va = "top"

        ax.annotate(
            f"N{number}",
            (x, y),
            xytext=offset,
            textcoords="offset points",
            ha="center",
            va=va,
            fontsize=10,
            weight="bold",
            zorder=3,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=0.6)
        )

    # --------------------------------------------------------
    # Legend definition
    # --------------------------------------------------------
    legend_handles = [
        Line2D([0], [0], color="red", lw=3, label="Tension"),
        Line2D([0], [0], color="blue", lw=3, label="Compression"),
        Line2D([0], [0], color="gray", lw=3, label="~ Zero")
    ]

    ax.legend(
        handles=legend_handles,
        loc="upper right",
        fontsize=9,
        frameon=True
    )

    # --------------------------------------------------------
    # Axes formatting
    # --------------------------------------------------------
    x_min, x_max = np.min(x_points), np.max(x_points)
    y_min, y_max = np.min(y_points), np.max(y_points)

    x_margin = max((x_max - x_min) * 0.05, 200)
    y_margin = max((y_max - y_min) * 0.15, 200)

    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_title("2D Truss - Axial Stress [MPa]")
    ax.margins(0)

    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

    ax.scatter(*fixed_node, marker="^", s=180, color="black")
    ax.scatter(*mobile_node, marker="s", s=100, color="green")

# ============================================================
# INPUT FUNCTIONS
# ============================================================

def check_value_int (value, min_val, max_val):
        
    if min_val <= value <= max_val:
        return True
    else:
        print(f"Error: The value has to be between {min_val} and {max_val}")
        return False

def ask_node_value (message, min_val, max_val):

    value = input(message).strip()

    # If the user writes "stop", it is returned inmediately
    if value.lower() == "stop":
        return "stop"

    # Format the user has to follow.
    # \d+ : searches for numbers. Parenthesis is added to form group 1 and 2.
    # \( and \): so that the program doesnt ignore them
    # ^ format starts at the beggining of the text
    # $ Sign to end the chain so that it doesnt accept anything later than the parenthesis is incorrect (20,10)
    format = r"^\(\s*([+-]?\d+)\s*,\s*([+-]?\d+)\s*\)$"

    # Checks the input        
    m = re.match(format,value)

    if m:
        try:
            value_in_X = int(m.group(1))
            value_in_Y = int(m.group(2))

            if check_value_int(value_in_X, min_val, max_val) and check_value_int(value_in_Y, min_val, max_val):
                return (value_in_X, value_in_Y)
            else:
                return None

        except ValueError:
            print("Error: Please, introduce correct integers.")
            return None      
    else:
        print("Error: Please, introduce the correct format (a,b) (spaces are allowed).")
        return None

def ask_element_order(message, n_nodes):

    value = input(message).strip()

    # Same format as with nodes
    format = r"^\(\s*(\d+)\s*,\s*(\d+)\s*\)$"

    # Checks the input        
    m = re.match(format,value)

    if m:
            try:
                element_1 = int(m.group(1)) 
                element_2 = int(m.group(2))  
    
                if check_value_int(element_1, 1, n_nodes) and check_value_int(element_2, 1, n_nodes):
                    return (element_1, element_2)
                else:
                    return None
    
            except ValueError:
                print("Error: Please, introduce correct integers.")
                return None      
    else:
        print("Error: Please, introduce the correct format (a,b) (spaces are allowed).")
        return None

def check_inverse_order(elements,element_input):

    inverse_element = (element_input[1], element_input[0])

    return inverse_element in elements

# ============================================================
# DEGREES OF FREEDOM
# ============================================================

def search_free_dof(dof, nodes, fixed_node, mobile_node):

    # --------------------------------------------------------
    # Search for restricted and free dofs
    # --------------------------------------------------------
    free_dofs = []
    
    restricted_dofs=[]
    
    for i, node in enumerate(nodes):
        
        if node == fixed_node: 

            fixed_dof_x = dof[i][0]
            fixed_dof_y = dof[i][1]

            fixed_dof = [fixed_dof_x-1, fixed_dof_y-1]

            restricted_dofs.append(fixed_dof_x)
            restricted_dofs.append(fixed_dof_y)

        elif node == mobile_node:

            mobile_dof = dof[i][0]
            fixed_mobile_dof = dof[i][1]

            fixed_mobile_dof_matrix = dof[i][1] - 1

            free_dofs.append(mobile_dof)
            restricted_dofs.append(fixed_mobile_dof)
            
        else:
            free_dof_x = dof[i][0]
            free_dof_y = dof[i][1]
            
            free_dofs.append(free_dof_x)
            free_dofs.append(free_dof_y)


    # --------------------------------------------------------
    # ADJUST VALUES FOR MATRIX
    # --------------------------------------------------------
    # ---- Restricted dofs ----

    restricted_dofs_length = len (restricted_dofs)
    print("\n--------------------------------------------------------\n")
    print(f"The restricted DoF are:\n{restricted_dofs}")
    matrix_restricted_dofs = restricted_dofs - (np.ones(restricted_dofs_length, dtype=int))
    
    # ---- Free dofs ----

    free_dofs_length = len (free_dofs)
    print(f"The free DoF are:\n{free_dofs}")
    matrix_free_dofs = free_dofs - (np.ones(free_dofs_length, dtype=int))
    print("\n--------------------------------------------------------")

    return matrix_restricted_dofs, matrix_free_dofs, fixed_dof, fixed_mobile_dof_matrix

# ============================================================
# MAIN
# ============================================================

def main(show_plot=True, plot_path=None):

    print("\n====================================")
    print("2D TRUSS SOLVER")
    print("====================================")

    # --------------------------------------------------------
    # Start interactive plot
    # --------------------------------------------------------
    
    fig, ax, _ = (initialize_dynamic_plot(max_length=1000))
    
    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    node_input= " "
    nodes = []

    print("\nNode input: ")
    while (node_input != "stop"):

        node_input = ask_node_value("Enter a node in the form of (a,b) in mm. Write 'stop' to end: ", node_min_value, node_max_value)

        if (node_input is not None and node_input != "stop"):
            if node_input in nodes:
                print(f"Error. The node {node_input} has already been added.")
            else:
                print(f"Node accepted: {node_input}")
                nodes.append(node_input)

    if len(nodes) < 2:
        raise ValueError("At least two distinct nodes are required.")

    print("\n--------------------------------------------------\n")
    print(f"Current nodes list is the following:\n{nodes}")

    n_nodes = len(nodes)

    print(f"Number of nodes: {n_nodes}")
    
    # Degrees of freedom are one-based here; NumPy indices are zero-based.
    nodes_dof = []
    for n in range(1, n_nodes + 1):
        nodes_dof.append((2 * n - 1, 2 * n))
    print("Total Degrees of Freedom [DoF]:")
    print (f"{nodes_dof}\n")
    print("--------------------------------------------------")
    # ----- Asking for restricted nodes -----
    
    # Fixed node
    while True:
        fixed_node = ask_node_value("\nWhich is the fixed node? Add it in the form of (a,b) in mm. : ", node_min_value, node_max_value)
        
        if fixed_node is not None and fixed_node in nodes:
            print(f"Node accepted: {fixed_node}")
            break
        else:
            print("Invalid node or not found in nodes list. Please try again.")

    # Mobile node
    while True:
        mobile_node = ask_node_value("Which is the mobile node? Add it in the form of (a,b) in mm. : ", node_min_value, node_max_value)
        
        if mobile_node is not None and mobile_node in nodes:
            if mobile_node != fixed_node:
                print(f"Node accepted: {mobile_node}\n")
                break  
            else:
                print("The mobile node cannot be the same as the fixed node.")
        else:
            print("Invalid node or not found in nodes list. Please try again.")
 
    
    # --------------------------------------------------------
    # Elements
    # --------------------------------------------------------

    # Element-count constraint for this educational interface.
    # This count does not guarantee stability.
    # n_elements = 2 * n_nodes - r
    # r = 3, number of reactions ( 1 fixed, 1 mobile)
    
    n_reactions = 3 
    n_elements = 2 * n_nodes - n_reactions

    print("--------------------------------------------------")
    print(f"\nThis interface requires {n_elements} elements; stability also depends on geometry and supports.")
    
    # Connectivity between nodes
    elements = []
    i = 0

    while (i < n_elements):
        
        element_order = ask_element_order("Enter the order of the elements in the form of (1,2): ", n_nodes)

        if (element_order is None):
            continue
        
        if(element_order[0] == element_order[1]):
            print("Error. A link cannot connect a node to itself.")
            continue

        if element_order in elements or check_inverse_order(elements,element_order):
            print(f"Error. The element {element_order} has already been added.")
            continue
                
        elements.append(element_order)
        i += 1

    print("\n--------------------------------------------------")        
    print(f"\nCurrent element list is the following:\n{elements}")
    print("\n--------------------------------------------------")


    elements_data = []
    
    for n, (i,j) in enumerate (elements, start = 1):

        # Obtain nodes
        node1 = nodes[max((i-1),0)]
        node2 = nodes[j-1]

        # Assign degrees of freedom
        element_dof = nodes_dof[max(i-1,0)] + nodes_dof[j-1]

        # Link characteristics
        length, l, m = orientation_between_links (node1, node2)

        print(f"\nThe link {n} connects {node1} and {node2}")
        print(f"Length: {length} Cos: {l} Sin: {m}")

        # Local stiffness_matrix
        k_local = stiffness_matrix (l, m , Area, E_Nmm2, length)

        element_data = {
            "id":n,
            "node_1": node1,
            "node_2": node2,
            "length":length,
            "cos_theta": l,
            "sen_theta": m,
            "K_local": k_local,
            "dof": element_dof
            }

        elements_data.append(element_data)

        print(element_data)

    # --------------------------------------------------------
    # Plot nodes and elements
    # --------------------------------------------------------

    draw_truss(ax, nodes, elements)

    # --------------------------------------------------------
    # Forces in the structure
    # --------------------------------------------------------

    node_loads = []
    i=0
    print("\n--------------------------------------------------\n")
    print("Building up the force vector:")
    while (i < n_nodes):
            
            force_in_node = ask_node_value(f"Add the load for node {nodes[i]} in the form of (a,b) in N : ", force_min_value, force_max_value)
    
            if (force_in_node is not None and force_in_node != "stop"):
                node_loads.append(force_in_node)
                i = i + 1

    force_vector = np.asarray(node_loads, dtype=float).reshape(-1)

    # --------------------------------------------------------
    # Plot forces and restricted nodes
    # --------------------------------------------------------
    print("Applied loads [N], in node order:")
    print(pd.DataFrame(node_loads, columns=["Fx [N]", "Fy [N]"],
                       index=np.arange(1, n_nodes + 1)).to_string())
    ax.scatter(*fixed_node, marker="^", s=180, color="black", label="Pinned support")
    ax.scatter(*mobile_node, marker="s", s=100, color="green", label="Roller: uy = 0")
    span = max(np.ptp(np.asarray(nodes), axis=0).max(), 1.0)
    for node, load in zip(nodes, node_loads):
        if np.linalg.norm(load) > 0:
            direction = np.asarray(load) / np.linalg.norm(load) * span * 0.18
            tip = np.asarray(node) + direction
            ax.annotate("", xy=tip, xytext=node, arrowprops={"arrowstyle": "->", "color": "red", "lw": 2})
            ax.annotate(f"F = {load} N", xy=tip, xytext=(5, 5), textcoords="offset points", color="red")
    ax.margins(0.3)
    ax.legend(loc="best")
    if plot_path is not None:
        Path(plot_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(plot_path, dpi=180, bbox_inches="tight")
    print("\n--------------------------------------------------\n")
    # --------------------------------------------------------
    # Global Stiffness Matrix
    # --------------------------------------------------------

    global_size = 2 * len(nodes)
    local_size = 4 
    
    k_global = np.zeros ((global_size , global_size))

    for element in range(0, n_elements):

        added_kt_local = elements_data[element]["K_local"]
        added_dof = np.array(elements_data[element]["dof"])

        matrix_dof = added_dof - (1,1,1,1)
        
        k_global[np.ix_(matrix_dof , matrix_dof )] += added_kt_local

    k_global_panda = pd.DataFrame(k_global)

    # --------------------------------------------------------
    # Solve the system F = k * x
    # --------------------------------------------------------
    print("Global stiffness Matrix:\n")
    print(k_global_panda)

    # Search for free dof
    restricted_dof, free_dof, fixed_dof, fixed_mobile_dof = search_free_dof(nodes_dof, nodes, fixed_node, mobile_node)

    # Reduce the global stiffness matrix and force vector
    reduced_k = k_global[np.ix_(free_dof, free_dof)]
    reduced_force = force_vector[free_dof]
    print("Solving the system:\n")
    print("Reduced stiffness matrix:")
    k_reduced_panda = pd.DataFrame(reduced_k)
    print(f"\n{k_reduced_panda}")

    print("\nReduced force matrix:")
    reduced_force_panda = pd.DataFrame(reduced_force)
    print(f"\n{reduced_force_panda}")

    # Only solve for the free dofs
    try:
        
        if np.linalg.matrix_rank(reduced_k) < len(free_dof):
            raise np.linalg.LinAlgError("Unstable or numerically rank-deficient model")
        x_free = np.linalg.solve(reduced_k, reduced_force)

        # Rebuild the full displacement vector (with fixed dof )
        x_total = np.zeros(len(force_vector))
        x_total[free_dof] = x_free

        print("\nDisplacement vector:")
        print(f"\n{pd.DataFrame(x_total)}\n")

        # --------------------------------------------------------
        # Reactions
        # --------------------------------------------------------

        Reactions = k_global @ x_total - force_vector
        print("Reactions:")
        print(f"\n{pd.DataFrame(Reactions)}")
        

        # --------------------------------------------------------
        # Linked bar stress
        # --------------------------------------------------------

        print("\nLinked bar stress:")
        for element, element_data in enumerate(elements_data):

            dof = np.array(element_data["dof"])
            cos_theta = element_data["cos_theta"]
            sen_theta = element_data["sen_theta"]

            # Displacement in the link nodes
            q_l = np.array([
                x_total[dof[0]-1],
                x_total[dof[1]-1],
                x_total[dof[2]-1],
                x_total[dof[3]-1]
            ])

            T = np.array([-cos_theta, -sen_theta, cos_theta, sen_theta])

            stress_l = (E_Nmm2 / element_data["length"]) * np.dot(T, q_l)

            # Store the calculated stress in the original dictionary
            element_data["axial_stress"] = stress_l

            print(f"Stress at link {element + 1}: {stress_l:.6f} MPa")

        print("\n--------------------------------------------------\n")


        # --------------------------------------------------------
        # Draw resulting truss stresses
        # --------------------------------------------------------

        fig_stress, ax_stress = plt.subplots(figsize=(12, 4.5), constrained_layout=True)
        draw_truss_stresses(ax_stress, nodes, elements, elements_data,fixed_node,mobile_node)

        # --------------------------------------------------------
        # Summary
        # --------------------------------------------------------
        
        print("====================================")
        print("Nodes")
        print("====================================")
        nodes_headers = ["Node", "Location", "ux [mm]", "uy [mm]"]
        nodes_tabulate = []

        for  n, node in enumerate(nodes):

            dof_tabulate = nodes_dof[n]
            ux = x_total[dof_tabulate[0]-1]
            uy = x_total[dof_tabulate[1]-1]

            node_row = [n+1, node, ux, uy]

            nodes_tabulate.append(node_row)

        print(tabulate(nodes_tabulate, headers = nodes_headers, tablefmt = "github",floatfmt=".6f"))

        print("\n====================================")
        print("Support reactions")
        print("====================================")
        reactions_headers = ["Support", "Node [mm]" , "Rx [N]", "Ry [N]"]

        fixed_reaction = Reactions [fixed_dof]
        mobile_reaction = Reactions [fixed_mobile_dof]
        reactions_table = [["Fixed node", fixed_node, fixed_reaction[0], fixed_reaction[1]],["Mobile node",mobile_node,"---",mobile_reaction]]
        print(tabulate(reactions_table, headers = reactions_headers, tablefmt = "github", floatfmt=".6f"))
        
        print("\n====================================")
        print("Elements")
        print("====================================")
            
        data_to_tabulate = ["id", "node_1", "node_2", "length", "axial_stress"]
        elements_tabulate= []
        
        for element_data in elements_data:
            row = [element_data[key] for key in data_to_tabulate]
            elements_tabulate.append(row)    
        
        element_headers = ["Element" , "Starting node [mm]", "Ending node [mm]", "Length [mm]", "Axial Stress[MPa]"]
        print(tabulate(elements_tabulate, headers=element_headers, tablefmt="github", floatfmt=".6f"))
            

        plt.ioff()
        if show_plot:

            #Refresh plots
            fig.canvas.draw_idle()
            fig_stress.canvas.draw_idle()

            #Block program execution until all plot windows are closed
            plt.show(block=True)
            
            plt.show()
        else:
            plt.close(fig)
            plt.close(fig_stress)
        return {"nodes": nodes, "elements": elements_data, "loads": force_vector,
                "displacements": x_total, "reactions": Reactions,
                "stiffness": k_global, "free_dof": free_dof,
                "node_rows": nodes_tabulate, "reaction_rows": reactions_table}

    except np.linalg.LinAlgError:
        print("ERROR: The system can not be solve because there is a singularity")
        plt.ioff()
        plt.close(fig)
        raise ValueError("The structure is unstable or numerically singular.") from None

if __name__ == "__main__":
    try:
        main()
    except (ValueError, EOFError, KeyboardInterrupt) as exc:
        print(f"Stopped: {exc}")
        raise SystemExit(1)
