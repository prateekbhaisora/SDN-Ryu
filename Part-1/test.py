from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0

class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER) # This decorator tells when below function will be called
    def packet_in_handler(self, ev):  # This method will be called only when Ryu receives an OpenFlow packet_in message
        msg = ev.msg #represents packet_in data structure
        dp = msg.datapath #msg.dp is an object that represents a datapath (switch)
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser #dp.ofproto and dp.ofproto_parser are objects that represent the OpenFlow protocol that Ryu and the switch negotiated.

        actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)] #OFPActionOutput class is used with a packet_out message to specify a switch port that you want to send the packet out of. This application uses the OFPP_FLOOD flag to indicate that the packet should be sent out on all ports.

        data = None
        if msg.buffer_id == ofp.OFP_NO_BUFFER: 
            data = msg.data

        out = ofp_parser.OFPPacketOut( #OFPPacketOut class is used to build a packet_out message
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data = data)
        dp.send_msg(out) #If you call Datapath class's send_msg method with a OpenFlow message class object, Ryu builds and sends the on-wire data format to the switch.