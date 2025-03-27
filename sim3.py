import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ResourceAllocationGraph:
    def __init__(self, root):
        self.graph = nx.DiGraph()
        self.root = root
        self.root.title("Resource Allocation Graph Simulator")

        # Setup matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control panel
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Process controls
        tk.Label(self.controls_frame, text="Process:").grid(row=0, column=0, padx=5, pady=5)
        self.process_entry = tk.Entry(self.controls_frame, width=15)
        self.process_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add", command=self.add_process).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove", command=self.remove_process, bg='lightcoral').grid(row=0, column=3, padx=5, pady=5)

        # Resource controls
        tk.Label(self.controls_frame, text="Resource:").grid(row=1, column=0, padx=5, pady=5)
        self.resource_entry = tk.Entry(self.controls_frame, width=15)
        self.resource_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add", command=self.add_resource).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove", command=self.remove_resource, bg='lightcoral').grid(row=1, column=3, padx=5, pady=5)

        # Request edge controls
        tk.Label(self.controls_frame, text="Request Edge (P → R):").grid(row=2, column=0, padx=5, pady=5)
        self.request_p_entry = tk.Entry(self.controls_frame, width=7)
        self.request_p_entry.grid(row=2, column=1, padx=5, pady=5)
        self.request_r_entry = tk.Entry(self.controls_frame, width=7)
        self.request_r_entry.grid(row=2, column=2, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add", command=self.request_resource).grid(row=2, column=3, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove", command=self.remove_request_edge, bg='lightcoral').grid(row=2, column=4, padx=5, pady=5)

        # Allocation edge controls
        tk.Label(self.controls_frame, text="Allocation Edge (R → P):").grid(row=3, column=0, padx=5, pady=5)
        self.allocate_r_entry = tk.Entry(self.controls_frame, width=7)
        self.allocate_r_entry.grid(row=3, column=1, padx=5, pady=5)
        self.allocate_p_entry = tk.Entry(self.controls_frame, width=7)
        self.allocate_p_entry.grid(row=3, column=2, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add", command=self.allocate_resource).grid(row=3, column=3, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove", command=self.remove_allocation_edge, bg='lightcoral').grid(row=3, column=4, padx=5, pady=5)

        # Deadlock detection
        tk.Button(self.controls_frame, text="Check Deadlock", command=self.check_deadlock, bg='lightcoral').grid(row=4, column=1, columnspan=2, pady=10)

        # Initialize with empty graph
        self.draw_graph()

    def add_process(self):
        process = self.process_entry.get().strip()
        if process and not self.graph.has_node(process):
            self.graph.add_node(process, type='process')
            self.draw_graph()

    def remove_process(self):
        process = self.process_entry.get().strip()
        if process in self.graph:
            self.graph.remove_node(process)
            self.draw_graph()

    def add_resource(self):
        resource = self.resource_entry.get().strip()
        if resource and not self.graph.has_node(resource):
            self.graph.add_node(resource, type='resource')
            self.draw_graph()

    def remove_resource(self):
        resource = self.resource_entry.get().strip()
        if resource in self.graph:
            self.graph.remove_node(resource)
            self.draw_graph()

    def request_resource(self):
        process = self.request_p_entry.get().strip()
        resource = self.request_r_entry.get().strip()
        if process and resource and self.graph.has_node(process) and self.graph.has_node(resource):
            self.graph.add_edge(process, resource, style='dashed', color='red')
            self.draw_graph()

    def remove_request_edge(self):
        process = self.request_p_entry.get().strip()
        resource = self.request_r_entry.get().strip()
        if self.graph.has_edge(process, resource):
            self.graph.remove_edge(process, resource)
            self.draw_graph()

    def allocate_resource(self):
        resource = self.allocate_r_entry.get().strip()
        process = self.allocate_p_entry.get().strip()
        if resource and process and self.graph.has_node(resource) and self.graph.has_node(process):
            self.graph.add_edge(resource, process, style='solid', color='blue')
            self.draw_graph()

    def remove_allocation_edge(self):
        resource = self.allocate_r_entry.get().strip()
        process = self.allocate_p_entry.get().strip()
        if self.graph.has_edge(resource, process):
            self.graph.remove_edge(resource, process)
            self.draw_graph()

    def check_deadlock(self):
        try:
            cycle = list(nx.find_cycle(self.graph, orientation='original'))
            if cycle:
                for u, v in cycle:
                    self.graph[u][v]['color'] = 'red'
                self.draw_graph()
                messagebox.showwarning("Deadlock Detected", f"Deadlock found in cycle: {cycle}")
            else:
                messagebox.showinfo("No Deadlock", "The system is deadlock-free")
        except nx.NetworkXNoCycle:
            messagebox.showinfo("No Deadlock", "The system is deadlock-free")
        except Exception as e:
            messagebox.showerror("Error", f"Error checking for deadlock: {str(e)}")

    def draw_graph(self):
        self.ax.clear()

        if not self.graph.nodes():
            self.ax.text(0.5, 0.5, "Add processes and resources to begin", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return

        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)

        process_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'process']
        resource_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'resource']

        nx.draw_networkx_nodes(self.graph, pos, nodelist=process_nodes, node_color='skyblue', node_size=800, ax=self.ax)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=resource_nodes, node_color='lightgreen', node_size=800, ax=self.ax)

        edges = self.graph.edges(data=True)
        for u, v, d in edges:
            color = d.get('color', 'black')
            style = d.get('style', 'solid')
            nx.draw_networkx_edges(self.graph, pos, edgelist=[(u, v)], edge_color=color, style=style, ax=self.ax)

        nx.draw_networkx_labels(self.graph, pos, ax=self.ax)

        self.ax.set_title("Resource Allocation Graph")
        self.ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()


root = tk.Tk()
app = ResourceAllocationGraph(root)
root.mainloop()