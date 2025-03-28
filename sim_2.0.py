import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import time
import threading
from collections import deque

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
        
        # Edge controls
        tk.Label(self.controls_frame, text="From:").grid(row=2, column=0, padx=5, pady=5)
        self.from_entry = tk.Entry(self.controls_frame, width=15)
        self.from_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.controls_frame, text="To:").grid(row=2, column=2, padx=5, pady=5)
        self.to_entry = tk.Entry(self.controls_frame, width=15)
        self.to_entry.grid(row=2, column=3, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add Request", command=self.add_request_edge, bg='lightyellow').grid(row=2, column=4, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Add Allocation", command=self.add_allocation_edge, bg='lightgreen').grid(row=2, column=5, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove Edge", command=self.remove_edge, bg='lightcoral').grid(row=2, column=6, padx=5, pady=5)
        
        # Deadlock detection
        tk.Button(self.controls_frame, text="Check Deadlock", command=self.check_deadlock, bg='orange').grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(self.controls_frame, text="Remove All", command=self.remove_all, bg='red').grid(row=3, column=2, columnspan=2, padx=5, pady=5)
        
        # Performance metrics
        self.metrics_frame = tk.Frame(root, bd=2, relief=tk.SUNKEN, padx=10, pady=10)
        self.metrics_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self.metrics_frame, text="Performance Metrics", font=("Arial", 12, "bold")).pack()
        self.cpu_label = tk.Label(self.metrics_frame, text="CPU Utilization: - %")
        self.cpu_label.pack()
        self.memory_label = tk.Label(self.metrics_frame, text="Memory Utilization: - %")
        self.memory_label.pack()
        self.page_fault_label = tk.Label(self.metrics_frame, text="Page Fault Rate: -")
        self.page_fault_label.pack()
        self.throughput_label = tk.Label(self.metrics_frame, text="Throughput: - processes/sec")
        self.throughput_label.pack()
        self.response_time_label = tk.Label(self.metrics_frame, text="Response Time: - sec")
        self.response_time_label.pack()
        
        self.processed_tasks = 0
        self.start_time = time.time()
        threading.Thread(target=self.update_metrics, daemon=True).start()
        
        self.draw_graph()
    
    def update_metrics(self):
        while True:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            page_fault_rate = round(psutil.swap_memory().sin / 1024, 2)
            elapsed_time = time.time() - self.start_time
            throughput = round(self.processed_tasks / elapsed_time, 2) if elapsed_time > 0 else 0
            response_time = round(elapsed_time / (self.processed_tasks + 1), 2)
            
            self.cpu_label.config(text=f"CPU Utilization: {cpu_usage} %")
            self.memory_label.config(text=f"Memory Utilization: {memory_usage} %")
            self.page_fault_label.config(text=f"Page Fault Rate: {page_fault_rate} KB/sec")
            self.throughput_label.config(text=f"Throughput: {throughput} processes/sec")
            self.response_time_label.config(text=f"Response Time: {response_time} sec")
            
            time.sleep(1)
    
    def add_process(self):
        process = self.process_entry.get().strip()
        if process and not self.graph.has_node(process):
            self.graph.add_node(process, type='process')
            self.processed_tasks += 1
            self.draw_graph()
    
    def remove_process(self):
        process = self.process_entry.get().strip()
        if process in self.graph:
            self.graph.remove_node(process)
            self.draw_graph()
    
    def add_resource(self):
        resource = self.resource_entry.get().strip()
        if resource and not self.graph.has_node(resource):
            self.graph.add_node(resource, type='resource', instances=1)  # Automatically set instances to 1
            self.draw_graph()
    
    def remove_resource(self):
        resource = self.resource_entry.get().strip()
        if resource in self.graph:
            self.graph.remove_node(resource)
            self.draw_graph()
    
    def add_request_edge(self):
        from_node = self.from_entry.get().strip()
        to_node = self.to_entry.get().strip()
        if from_node in self.graph and to_node in self.graph:
            if self.graph.nodes[from_node]['type'] == 'process' and self.graph.nodes[to_node]['type'] == 'resource':
                self.graph.add_edge(from_node, to_node, type='request')
                self.draw_graph()
            else:
                messagebox.showerror("Error", "Request edge must go from process to resource")
    
    def add_allocation_edge(self):
        from_node = self.from_entry.get().strip()
        to_node = self.to_entry.get().strip()
        if from_node in self.graph and to_node in self.graph:
            if self.graph.nodes[from_node]['type'] == 'resource' and self.graph.nodes[to_node]['type'] == 'process':
                self.graph.add_edge(from_node, to_node, type='allocation')
                self.draw_graph()
            else:
                messagebox.showerror("Error", "Allocation edge must go from resource to process")
    
    def remove_edge(self):
        from_node = self.from_entry.get().strip()
        to_node = self.to_entry.get().strip()
        if from_node in self.graph and to_node in self.graph and self.graph.has_edge(from_node, to_node):
            self.graph.remove_edge(from_node, to_node)
            self.draw_graph()
    
    
    def check_deadlock(self):
        try:
            # Separate processes and resources
            processes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'process']
            resources = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'resource']
            
            # Create a graph to track dependencies
            dependency_graph = nx.DiGraph()
            
            # Analyze resource allocation and request edges
            for p in processes:
                # Find resources requested by the process
                requested_resources = [r for r in resources if self.graph.has_edge(p, r)]
                
                # Find resources allocated to the process
                allocated_resources = [r for r in resources if self.graph.has_edge(r, p)]
                
                # For each requested resource not allocated to the process
                for req_resource in requested_resources:
                    # Find which process currently holds this resource
                    resource_holders = [p2 for p2 in processes if self.graph.has_edge(req_resource, p2)]
                    
                    # Add dependency edges
                    for holder in resource_holders:
                        if holder != p:
                            dependency_graph.add_edge(p, holder)
            
            # Check for cycles in the dependency graph
            try:
                cycle = list(nx.find_cycle(dependency_graph, orientation='original'))
                
                # Construct the cycle of process names
                cycle_nodes = [edge[0] for edge in cycle] + [cycle[0][0]]  # Complete the cycle
                
                # Highlight the cycle and show warning
                messagebox.showwarning("Deadlock Detected", 
                    f"Deadlock found in cycle: {' → '.join(cycle_nodes)}")
                self.highlight_cycle(cycle)
                
            except nx.NetworkXNoCycle:
                messagebox.showinfo("No Deadlock", "No deadlock detected in the system")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error checking for deadlock: {str(e)}")
        
    def highlight_cycle(self, cycle):
        self.ax.clear()
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        
        # Get all nodes and edges involved in the cycle
        cycle_nodes = set()
        cycle_edges = set()
        for edge in cycle:
            cycle_nodes.add(edge[0])
            cycle_nodes.add(edge[1])
            cycle_edges.add((edge[0], edge[1]))
        
        # Draw all nodes
        process_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'process']
        resource_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'resource']
        
        # Draw non-cycle nodes normally
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[n for n in process_nodes if n not in cycle_nodes], 
                              node_color='skyblue', node_size=800, ax=self.ax)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[n for n in resource_nodes if n not in cycle_nodes], 
                              node_color='lightgreen', node_size=800, ax=self.ax)
        
        # Highlight cycle nodes
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[n for n in process_nodes if n in cycle_nodes], 
                              node_color='red', node_size=1000, ax=self.ax)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=[n for n in resource_nodes if n in cycle_nodes], 
                              node_color='red', node_size=1000, ax=self.ax)
        
        # Draw all edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=[e for e in self.graph.edges() if e not in cycle_edges], 
                              arrowstyle='->', arrowsize=20, ax=self.ax)
        
        # Highlight cycle edges
        nx.draw_networkx_edges(self.graph, pos, edgelist=[e for e in self.graph.edges() if e in cycle_edges], 
                              edge_color='red', width=3, arrowstyle='->', arrowsize=20, ax=self.ax)
        
        nx.draw_networkx_labels(self.graph, pos, ax=self.ax)
        self.ax.set_title("Resource Allocation Graph (Deadlock Detected)")
        self.ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()
    
    def remove_all(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove all nodes and edges?"):
            self.graph.clear()
            self.draw_graph()
    
    def draw_graph(self):
        self.ax.clear()
        if not self.graph.nodes():
            self.ax.text(0.5, 0.5, "Add processes and resources to begin", ha='center', va='center', fontsize=12)
            self.canvas.draw()
            return
        
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        process_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'process']
        resource_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get('type') == 'resource']
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, nodelist=process_nodes, node_color='skyblue', node_size=800, ax=self.ax)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=resource_nodes, node_color='lightgreen', node_size=800, ax=self.ax)
        
        # Draw edges with different styles for request and allocation
        request_edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('type') == 'request']
        allocation_edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('type') == 'allocation']
        
        nx.draw_networkx_edges(self.graph, pos, edgelist=request_edges, edge_color='orange', 
                              style='dashed', arrowstyle='->', arrowsize=20, ax=self.ax)
        nx.draw_networkx_edges(self.graph, pos, edgelist=allocation_edges, edge_color='green', 
                              arrowstyle='->', arrowsize=20, ax=self.ax)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, ax=self.ax)
        
        # Add legend
        self.ax.plot([], [], color='orange', linestyle='dashed', label='Request Edge')
        self.ax.plot([], [], color='green', label='Allocation Edge')
        self.ax.legend(loc='upper right')
        
        self.ax.set_title("Resource Allocation Graph")
        self.ax.axis('off')
        self.figure.tight_layout()
        self.canvas.draw()

root = tk.Tk()
app = ResourceAllocationGraph(root)
root.mainloop()