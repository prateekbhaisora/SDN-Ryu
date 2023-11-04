from mininet.topo import Topo

class MyTopo( Topo ):

    def build( self ):
    
        Host1 = self.addHost( 'Host1' )
        Host2 = self.addHost( 'Host2' )
        Host3 = self.addHost( 'Host3' )
        Host4 = self.addHost( 'Host4' )
        Host5 = self.addHost( 'Host5' )
        Switch1 = self.addSwitch( 'Switch1' )
        Switch2 = self.addSwitch( 'Switch2' )

        self.addLink( Host1, Switch1 )
        self.addLink( Host2, Switch1 )
        self.addLink( Host3, Switch1 )
        self.addLink( Switch1, Switch2 )
        self.addLink( Switch2, Host4 )
        self.addLink( Switch2, Host5 )

topos = { 'mytopo': ( lambda: MyTopo() ) }