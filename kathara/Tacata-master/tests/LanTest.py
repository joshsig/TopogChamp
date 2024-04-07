import unittest
from tacata import Lan
from tacata import Interface

class LanTest(unittest.TestCase):
    def getIface(self, ip):
        # utility
        iface = Interface(None, "0")
        iface.setIp(ip)
        return iface

    def setUp(self):
        self.lan = Lan(None, "lan")
        initialIface = Interface(None, "0")
        initialIface.setIp("192.168.1.1/24")
        self.lan.addInterface(initialIface)

    def test_sameIp(self):
        iface = self.getIface("192.168.1.1/24")
        self.lan.addInterface(iface)
        # no exception should be raised

    def test_samePrefixDifferentIp(self):
        iface = self.getIface("192.168.1.255/24")
        self.lan.addInterface(iface)
        # no exception should be raised

    def test_samePrefixDifferentLength(self):
        iface = self.getIface("192.168.1.1/25")
        self.assertRaises(Exception, self.lan.addInterface, iface)

    def test_differentPrefixSameLength(self):
        iface = self.getIface("192.168.2.1/24")
        self.assertRaises(Exception, self.lan.addInterface, iface)
        
    # some advanced test to be sure...
    def test_samePrefixDifferentIp_2(self):
        lan = Lan(None, "l")
        lan.addInterface(self.getIface("192.168.1.128/25"))
        lan.addInterface(self.getIface("192.168.1.130/25"))
        # no exception should be raised

    def test_differentPrefixSameLength_2(self):
        lan = Lan(None, "l")
        lan.addInterface(self.getIface("192.168.1.128/25"))
        self.assertRaises(Exception, lan.addInterface, self.getIface("192.168.1.127/25"))

if __name__ == "__main__":
    unittest.main()
        