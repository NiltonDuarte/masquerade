
from math import *

"""
Class to calculate the values of W_a and W_b such
that \\frac{V_a}{V_b}=r holds aproximately in W integer
and maximaze the system troughput P_s
Based on Performance Analysis of the IEEE 802.11 Distributed Coordination Function - Giuseppe Bianchi
"""
class DCF_Otimizer:

    def __init__(self, rate):
        self.r = rate
        self.step = 5
        self.wa = 8.
        self.wb = 32.
        self.calc_wb()
        
        #medidas em us do padrao 802.11b, valores retirados da pagina 16 tese mestrado power evaluation[...]
        self.e_p = 1400*8/(1024.*1024.) #in megabit
        self.sigma = 20*0.000001 #in seconds
        self.T_s = 1515*0.000001
        self.T_c = 1281*0.000001

    def P_tr(self):
        #eq 10
        return 1-(1-self.tau_a())*(1-self.tau_b())

    def P_sa(self):
        #from eq 11
        return self.tau_a()*(1-self.tau_b())/self.P_tr()

    def P_sb(self):
        #from eq 11
        return self.tau_b()*(1-self.tau_a())/self.P_tr()

    def P_s(self):
        #from eq 11
        return self.P_sa()+self.P_sb()

    def tau_a(self):
        #eq 8
        return 2./(self.wa+1)

    def tau_b(self):
        #eq 8
        return 2./(self.wb+1)

    def calc_wb(self):
        self.wb = self.r*self.wa-self.r+1


    def S(self):
        #eq 25
        #self.calc_wb()
        numerador = self.e_p
        denomin_1 = self.T_s-self.T_c
        denomin_2 = ((self.sigma*(1-self.P_tr())/self.P_tr())+self.T_c)/self.P_s()
        return numerador/(denomin_1+denomin_2)

    def otim_fixedWb(self):
        delta = 0.001
        stop = False
        prevS=0
        currS = self.S()
        _iter = 0
        while True:
            _iter += 1
            prev_prevS=prevS
            prevS = currS
            self.wa = self.wa + self.step
            if self.wa < 2:
                self.wa = 2
                prevS = self.S()
                break
            currS = self.S()
            print "wa= {}, wb= {}, S= {}, step= {}, iter {}".format(self.wa, self.wb, currS, self.step, _iter)
            if abs(prevS - currS) < delta:
                break

            if prevS > currS:
                if abs(self.step)==1:
                    self.wa = self.wa - self.step
                    break;
                if self.step > 0:
                    self.step = -(self.step+1)/2
                else:
                    self.step = -(self.step/2)
                #self.step = -(self.step+(abs(self.step)/self.step))/2
        print "FINISHED wa= {}, wb= {}, S= {}, step= {}, iter {}".format(self.wa, self.wb, prevS, self.step, _iter)
        return prevS

    def otim_rate(self):
        delta = 0.001
        stop = False
        prevS=0
        self.calc_wb()
        currS = self.S()
        _iter = 0
        while True:
            _iter += 1
            prev_prevS=prevS
            prevS = currS
            self.wa = self.wa + self.step
            self.calc_wb()
            if self.wa < 2:
                self.wa = 2
                self.calc_wb()
                break
            currS = self.S()
            print "wa= {}, wb= {}, S= {}, step= {}, iter {}".format(self.wa, self.wb, currS, self.step, _iter)

            if abs(prevS - currS) < delta:
                break

            if prevS > currS:
                if abs(self.step)==1:
                    self.wa = self.wa - self.step
                    break
                if self.step > 0:
                    self.step = -(self.step+1)/2
                else:
                    self.step = -(self.step/2)
                #self.step = -(self.step+(abs(self.step)/self.step))/2

        wb = self.wb   
        self.wb = ceil(wb)
        cwb = self.S()
        self.wb = floor(wb)
        fwb = self.S()
        #check which ceilling or flooring the wb gives the best performance
        if cwb > fwb:
            self.wb = ceil(wb)
            ret = cwb
        else:
            self.wb = floor(wb)
            ret = fwb
        print "FINISHED wa= {}, wb= {}, S= {}, step= {}, iter {}".format(self.wa, self.wb, ret, self.step, _iter)
        return ret
        

            



    def __call__(self):
        ret = self.otim_rate()
        print "wa={}, wb={}, S={}".format(self.wa, self.wb, ret)
        return ret
        
        #self.wa=22
        #self.calc_wb()
        #print self.S()

if __name__ == '__main__':
    otim = DCF_Otimizer(0.35)
    otim.wb = 18
    ret = otim.otim_fixedWb()
    print "==================================================="
    ret = otim.otim_rate()
    print "==================================================="
    otim.wa=2
    otim.calc_wb()
    curr=otim.S()

    for i in range(3,60):
        prev=curr
        otim.wa=i
        otim.calc_wb()
        curr=otim.S()
        
        print prev > curr , i, curr
    print "==================================================="
    otim.wa=2
    otim.wb=2
    curr=otim.S()

    for i in range(3,60):
        prev=curr
        otim.wa=i
        #otim.calc_wb()
        curr=otim.S()
        
        print prev > curr , i, curr

