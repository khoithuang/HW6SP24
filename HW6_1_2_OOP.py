# I got help from ChatGPT.
import numpy as np
from scipy.optimize import fsolve

class ResistorNetwork():
    #region constructor
    def __init__(self):
        """
        The resistor network consists of Loops, Resistors and Voltage Sources.
        This is the constructor for the network and it defines fields for Loops, Resistors and Voltage Sources.
        You can populate these lists manually or read them in from a file.
        """
        #create some instance variables that are logical parts of a resistor network
        self.Loops = []  # initialize an empty list of loop objects in the network
        self.Resistors = []  # initialize an empty a list of resistor objects in the network
        self.VSources = []  # initialize an empty a list of source objects in the network
    #endregion

    #region methods/functions
    def BuildNetworkFromFile(self, filename):
        """
        This function reads the lines from a file and processes the file to populate the fields
        for Loops, Resistors and Voltage Sources
        :param filename: string for file to process
        :return: nothing
        """
        FileTxt = open(filename,"r").read().split('\n')  # reads from file and then splits the string at the new line characters
        LineNum = 0  # a counting variable to point to the line of text to be processed from FileTxt
        # erase any previous
        self.Resistors = []
        self.VSources = []
        self.Loops = []
        LineNum = 0
        lineTxt = ""
        FileLength = len(FileTxt)
        while LineNum < FileLength:
            lineTxt = FileTxt[LineNum].lower().strip()
            if len(lineTxt) <1:
                pass # skip
            elif lineTxt[0] == '#':
                pass  # skips comment lines
            elif "resistor" in lineTxt:
                LineNum = self.MakeResistor(LineNum, FileTxt)
            elif "source" in lineTxt:
                LineNum = self.MakeVSource(LineNum, FileTxt)
            elif "loop" in lineTxt:
                LineNum = self.MakeLoop(LineNum, FileTxt)
            LineNum+=1
        pass

    def MakeResistor(self, N, Txt):
        """
        Make a resistor object from reading the text file starting after detecting '<resistor>' in the text file.
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        R = Resistor()
        N += 1  # <Resistor> was detected, so move to next line in Txt
        txt = Txt[N].lower()
        while "resistor" not in txt:
            if "name" in txt:
                R.Name = txt.split('=')[1].strip()
            if "resistance" in txt:
                R.Resistance = float(txt.split('=')[1].strip())
            N+=1
            if N < len(Txt):
                txt = Txt[N].lower()
            else:
                break

        self.Resistors.append(R)  # append the resistor object to the list of resistors
        return N

    def MakeVSource (self, N, Txt):
        """
        Make a voltage source object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a voltage source object
        """
        VS = VoltageSource()
        N+=1
        if N < len(Txt):
            txt = Txt[N].lower()
        else:
            return N
        while "source" not in txt:
            if "name" in txt:
                VS.Name = txt.split('=')[1].strip()
            if "value" in txt:
                VS.Voltage = float(txt.split('=')[1].strip())
            if "type" in txt:
                VS.Type = txt.split('=')[1].strip()
            N+=1
            if N < len(Txt):
                txt = Txt[N].lower()
            else:
                break

        self.VSources.append(VS)
        return N

    def MakeLoop(self, N, Txt):
        """
        Make a Loop object from reading the text file
        :param N: (int) Line number for current processing
        :param Txt: [string] the lines of the text file
        :return: a resistor object
        """
        L = Loop()
        N+=1
        if N < len(Txt):
            txt = Txt[N].lower()
        else:
            return N
        while "loop" not in txt:
            if "name" in txt:
                L.Name = txt.split('=')[1].strip()
            if "nodes" in txt:
                txt = txt.replace(" ", "")
                L.Nodes = txt.split('=')[1].strip().split(',')
            N+=1
            if N < len(Txt):
                txt = Txt[N].lower()
            else:
                break

        self.Loops.append(L)
        return N

    def AnalyzeCircuit(self):
        """
        Use fsolve to find currents in the second resistor network.
        1. KCL:  The total current flowing into any node in the network is zero.
        2. KVL:  When traversing a closed loop in the circuit, the net voltage drop must be zero.
        :return: a list of the currents in the second resistor network
        """
        # need to set the currents to that Kirchoff's laws are satisfied
        i0 = np.ones(len(self.Resistors))  # define an initial guess for the currents in the circuit
        i = fsolve(self.GetKirchoffVals2, i0)
        # print output to the screen
        for idx, current in enumerate(i, 1):
            print("I{} = {:0.1f}".format(idx, current))
        return i

    def GetKirchoffVals2(self, i):
        """
        This function uses Kirchoff Voltage and Current laws to analyze the second circuit
        KVL:  The net voltage drop for a closed loop in a circuit should be zero
        KCL:  The net current flow into a node in a circuit should be zero
        :param i: a list of currents relevant to the circuit
        :return: a list of loop voltage drops and node currents
        """
        # set current in resistors in the top loop.
        self.GetResistorByName('ad').Current = i[0]  # I_1 in diagram
        self.GetResistorByName('bc').Current = i[0]  # I_1 in diagram
        self.GetResistorByName('cd').Current = i[2]  # I_3 in diagram
        # set current in resistor in bottom loop.
        self.GetResistorByName('ce').Current = i[1]  # I_2 in diagram
        # calculate net current into node c
        Node_c_Current = sum([i[0], i[1], -i[2]])

        KVL = self.GetLoopVoltageDrops()  # two equations here
        KVL.append(Node_c_Current)  # one equation here
        return KVL

    def GetElementDeltaV(self, name):
        """
        Need to retrieve either a resistor or a voltage source by name.
        :param name:
        :return:
        """
        for r in self.Resistors:
            if name == r.Name:
                return -r.DeltaV()
            if name[::-1] == r.Name:
                return -r.DeltaV()
        for v in self.VSources:
            if name == v.Name:
                return v.Voltage
            if name[::-1] == v.Name:
                return v.Voltage

    def GetLoopVoltageDrops(self):
        """
        This calculates the net voltage drop around a closed loop in a circuit based on the
        current flowing through resistors (cause a drop in voltage regardless of direction of traversal) or
        the value of the voltage source that have been set up as positive based on the direction of traversal.
        :return: net voltage drop for all loops in the network.
        """
        loopVoltages=[]
        for L in self.Loops:
            # Traverse loops in order of nodes and add up voltage drops between nodes
            loopDeltaV=0
            for n in range(len(L.Nodes)):
                if n == len(L.Nodes)-1:
                    name = L.Nodes[0] + L.Nodes[n]
                else:
                    name = L.Nodes[n]+L.Nodes[n+1]
                loopDeltaV += self.GetElementDeltaV(name)
            loopVoltages.append(loopDeltaV)
        return loopVoltages

    def GetResistorByName(self, name):
        """
        A way to retrieve a resistor object from self.Resistors based on resistor name
        :param name:
        :return:
        """
        for r in self.Resistors:
            if r.Name == name:
                return r

class Loop():
    #region constructor
    def __init__(self):
        """
        Defines a loop as a list of node names.
        """
        self.Nodes = []
    #endregion

class Resistor():
    #region  constructor
    def __init__(self, Resistance=1.0, Current=0.0, Name='ab'):
        """
        Defines a resistor to have a self.Resistance, self.Current, and self.Name instance variables.
        :param R: resistance in Ohm
        :param i: current in amps
        :param name: name of resistor by alphabetically ordered pair of node names
        """
        self.Resistance = Resistance
        self.Current = Current
        self.Name = Name
    #endregion

    #region methods/functions
    def DeltaV(self):
        """
        Calculates voltage change across resistor.
        :return: the signed value of voltage drop.  Voltage drop > 0 in direction of positive current flow.
        """
        return self.Current * self.Resistance
    #endregion

class VoltageSource():
    #region constructor
    def __init__(self, V=12.0, Name='ab'):
        """
        Define a voltage source with instance variables of self.Voltage = V, self.Name = name
        :param V: The voltage
        :param name: the name of voltage source.  The voltage source naming convention is to use the nodes such as 'ab'
        where the order of the nodes goes in the direction of positive voltage change as I traverse the loop from a to b.
        """
        self.Voltage = V
        self.Name = Name
    #endregion

# endregion Function Definitions
def main():
    """
    This program solves for the unknown currents in the circuits of the homework assignment.
    :return: nothing
    """
    Net1 = ResistorNetwork()  # Instantiate a resistor network object for the first circuit
    Net1.BuildNetworkFromFile("ResistorNetwork.txt")  # Build the resistor network from a text file for the first circuit
    IVals1 = Net1.AnalyzeCircuit()  # Analyze the first circuit

    Net2 = ResistorNetwork2()  # Instantiate a resistor network object for the second circuit
    Net2.BuildNetworkFromFile("ResistorNetwork2.txt")  # Build the resistor network from a text file for the second circuit
    IVals2 = Net2.AnalyzeCircuit()  # Analyze the second circuit

# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion
