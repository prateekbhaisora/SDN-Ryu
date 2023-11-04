from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class HubController(app_manager.RyuApp):
    # Specifies the OpenFlow version to use (v1.3)
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(HubController, self).__init__(*args, **kwargs)
        # Initialize a MAC address table (as a dictionary) to keep track of MAC addresses to port mappings.
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # This decorator registers the 'switch_features_handler' function to be called when
        # the specified event 'EventOFPSwitchFeatures' is triggered in the OpenFlow controller.
        # The 'CONFIG_DISPATCHER' context indicates that this function will be called during the
        # configuration phase.

        # Retrieve the Datapath object from the event message.
        datapath = ev.msg.datapath

        # Get the OpenFlow protocol version supported by the switch.
        ofproto = datapath.ofproto

        # Create a parser object for the specific OpenFlow version to build OpenFlow messages.
        parser = datapath.ofproto_parser

        # The purpose of this function is to set up initial configurations for the switch when
        # it connects to the controller, typically during the switch initialization phase.
        # In this case, it's used to install a table-miss flow entry, which directs traffic that
        # doesn't match any specific flow entries to be sent to the controller for further processing.

        # Create an empty match to match all packets (table-miss flow entry).
        match = parser.OFPMatch()

        # Define the action to be taken when a packet matches the table-miss entry. Here, it's
        # set to output the packet to the controller (OFP_ACTION_OUTPUT) without buffering
        # (OFP_NO_BUFFER).
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        # Call the 'add_flow' function to add the table-miss flow entry to the switch's flow table.
        self.add_flow(datapath, 0, match, actions)


        # Install a table-miss flow entry, directing traffic to the controller.
        match = parser.OFPMatch()  # Create an empty match, matching all packets.
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]  # Define the action to output to the controller.
        self.add_flow(datapath, 0, match, actions)  # Call the 'add_flow' function to install the flow entry.

        def add_flow(self, datapath, priority, match, actions):
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser

            # Construct a flow_mod message to add a flow entry to the switch's flow table.
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]  # Create an instruction to apply actions.
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)  # Create a flow_mod message.

            # Send the flow_mod message to the switch to add the specified flow entry.
            datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Get the Datapath ID (DPID) to identify OpenFlow switches.
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Analyze the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # Get the received port number from the packet_in message.
        in_port = msg.match['in_port']

        # Log information about the received packet.
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # Learn a MAC address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        # If the destination MAC address is already learned, decide which port to output the packet; otherwise, FLOOD.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # Construct an action list for packet forwarding.
        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid packet_in for the same destination address next time.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        # Construct a packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)
