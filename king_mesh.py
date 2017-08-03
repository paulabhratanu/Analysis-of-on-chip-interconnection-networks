from m5.params import *
from m5.objects import *

from BaseTopology import SimpleTopology

# Creates a generic Mesh assuming an equal number of cache
# and directory controllers.
# XY routing is enforced (using link weights)
# to guarantee deadlock freedom.

class king_mesh(SimpleTopology):
    description='king_mesh'

    def __init__(self, controllers):
        self.nodes = controllers

    # Makes a generic mesh
    # assuming an equal number of cache and directory cntrls

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_routers = options.num_cpus
        num_rows = options.mesh_rows

        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet


        # There must be an evenly divisible number of cntrls to routers
        # Also, obviously the number or rows must be <= the number of routers
        cntrls_per_router, remainder = divmod(len(nodes), num_routers)
        assert(num_rows > 0 and num_rows <= num_routers)
        num_columns = int(num_routers / num_rows)
        assert(num_columns * num_rows == num_routers)

        # Create the routers in the mesh
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        # Add all but the remainder nodes to the list of nodes to be uniformly
        # distributed across the network.
        network_nodes = []
        remainder_nodes = []
        for node_index in xrange(len(nodes)):
            if node_index < (len(nodes) - remainder):
                network_nodes.append(nodes[node_index])
            else:
                remainder_nodes.append(nodes[node_index])

        # Connect each node to the appropriate router
        ext_links = []
        for (i, n) in enumerate(network_nodes):
            cntrl_level, router_id = divmod(i, num_routers)
            assert(cntrl_level < cntrls_per_router)
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Connect the remainding nodes to router 0.  These should only be
        # DMA nodes.
        for (i, node) in enumerate(remainder_nodes):
            assert(node.type == 'DMA_Controller')
            assert(i < remainder)
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                    int_node=routers[0],
                                    latency = link_latency))
            link_count += 1

        network.ext_links = ext_links

        # Create the mesh links.
        int_links = []

        # East output to West input links (weight = 1)
        for row in xrange(num_rows):
            for col in xrange(num_columns):
                if (col + 1 < num_columns):
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[east_out],
                                             dst_node=routers[west_in],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency = link_latency,
                                             weight=1))
                    link_count += 1

        # West output to East input links (weight = 1)
        for row in xrange(num_rows):
            for col in xrange(num_columns):
                if (col + 1 < num_columns):
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[west_out],
                                             dst_node=routers[east_in],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency = link_latency,
                                             weight=1))
                    link_count += 1

        # North output to South input links (weight = 2)
        for col in xrange(num_columns):
            for row in xrange(num_rows):
                if (row + 1 < num_rows):
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north_out],
                                             dst_node=routers[south_in],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency = link_latency,
                                             weight=2))
                    link_count += 1

        # South output to North input links (weight = 2)
        for col in xrange(num_columns):
            for row in xrange(num_rows):
                if (row + 1 < num_rows):
                    north_in = col + (row * num_columns)
                    south_out = col + ((row + 1) * num_columns)
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[south_out],
                                             dst_node=routers[north_in],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency = link_latency,
                                             weight=2))
                    link_count += 1
       #East output to south_west input(weight=3)
		temp_1=num_rows+1
		i=1
		num=0
		for row in xrange(num_rows):
			for col in xrange(num_columns):
				if((col+i) < num_columns):
					east_out=row+num
					temp=east_out
					south_west_in=temp+temp_1
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[east_out],
											 dst_node=routers[south_west_in],
											 src_outport="South_west",
											 dst_inport="east_west",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+temp_1
			i=i+1
			num=0
			   #south_west output to east input(weight=3)
			i=1
			num=0
			for row in xrange(num_rows):
				for row in xrange(num_columns):
					if((col+1) < num_columns):
						east_in=row+num
						temp=east_in
						south_west_out=temp+temp_1
						int_links.append(IntLink(link_id=link_count,
												src_node=routers[south_west_out],
												dst_node=routers[east_in],
												src_outport="east_west",
												dst_inport="south_west",
												latency = link_latency,
												weight=3))
						link_count += 1
						num=num+5
			i=i+1
			num=0
  			
			#East output to south_west input(weight=3)
		j=2
		num=0
		for row in xrange(4,num_rows*3,4):
			for col in xrange(num_columns):
				if((col+j) < num_columns):
					east_out=row+num
					temp=east_out
					south_west_in=temp+temp_1
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[east_out],
											 dst_node=routers[south_west_in],
											 src_outport="South_west_1",
											 dst_inport="east_west_1",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+5
			j=j+1
			num=0
                   
			temp_1=num_rows+1
            #west input to north-east output
		i=1
		num=0
		temp_2=num_rows-1
		for row in xrange(num_rows-1,-1,-1):
			for col in xrange(num_columns):
				if((col+i) < num_columns):
					north_east_out=row+num
					temp=north_east_out
					west_in=temp+temp_2
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[north_east_out],
											 dst_node=routers[west_in],
											 src_outport="north_east_out",
											 dst_inport="west_in",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+temp_2
			i=i+1
			num=0

			#north-east input to west output
		i=1
		num=0
		temp_2=num_rows-1
		for row in xrange(num_rows-1,-1,-1):
			for col in xrange(num_columns):
				if((col+i) < num_columns):
					west_in=row+num
					temp=west_in
					north_east_out=temp+temp_2
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[west_in],
											 dst_node=routers[north_east_out],
											 src_outport="west_in",
											 dst_inport="north_east_out",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+temp_2
			i=i+1
			num=0
                #west-1 input to north-east-1 output
		j=2
		num=0
		total_size=num_rows*num_columns-1
		for row in xrange(7,total_size,4):
			for col in xrange(num_columns):
				if((col+j) < num_columns):
					north_east_out_1=row+num
					temp=north_east_out_1
					west_in_1=temp+temp_2
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[north_east_out_1],
											 dst_node=routers[west_in_1],
											 src_outport="north_east_out_1",
											 dst_inport="west_in_1",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+5
			j=j+1
			num=0
                   
			#north-east-1 input to west-1 output
		j=2
		num=0
		total_size=num_rows*num_columns-1
		for row in xrange(7,total_size,4):
			for col in xrange(num_columns):
				if((col+j) < num_columns):
					west_in_1=row+num
					temp=west_in_1
					north_east_out_1=temp+temp_2
					int_links.append(IntLink(link_id=link_count,
											 src_node=routers[west_in_1],
											 dst_node=routers[north_east_out_1],
											 src_outport="west_in_1",
											 dst_inport="north_east_out_1",
											 latency = link_latency,
											 weight=3))
					link_count += 1
					num=num+5
			j=j+1
			num=0
			

			network.int_links = int_links

					
