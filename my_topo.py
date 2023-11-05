from mininet.topo import Topo

class MyTopo( Topo ):

    def build( self ):
    
        Host1 = self.addHost( 'Host1' , ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        Host2 = self.addHost( 'Host2' , ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        Host3 = self.addHost( 'Host3' , ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        Host4 = self.addHost( 'Host4' , ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        Host5 = self.addHost( 'Host5' , ip='10.0.0.5/24', mac='00:00:00:00:00:05')
        Switch1 = self.addSwitch( 'Switch1' )
        Switch2 = self.addSwitch( 'Switch2' )

        self.addLink( Host1, Switch1 )
        self.addLink( Host2, Switch1 )
        self.addLink( Host3, Switch1 )
        self.addLink( Switch1, Switch2 )
        self.addLink( Switch2, Host4 )
        self.addLink( Switch2, Host5 )

topos = { 'mytopo': ( lambda: MyTopo() ) }
