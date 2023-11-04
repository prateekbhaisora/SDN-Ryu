from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_parser
from ryu.lib.packet import packet, ethernet

class HubController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(HubController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        # Get the received port number from the packet_in message.
        in_port = msg.match['in_port']

        # Create an action to output the packet to all ports except the incoming port.
        actions = [ofproto_parser.OFPActionOutput(ofproto.OFPP_FLOOD, ofproto.OFPCML_NO_BUFFER)]

        # Construct a packet_out message and send it.
        out = ofproto_parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)

        # Do not install any flow entries, as this is a hub behavior that doesn't involve learning.
