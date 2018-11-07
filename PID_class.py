class PID:
   'Common base class for all PIDs'
   

   def __init__(self, P, I, D, dt):
      self.P = P
      self.I = I
      self.D = D
      self.dt = dt
      
      
   def actuate(self,e,eant,eint,umax,umin):
#set variables
     kp=self.P
     ki=self.I
     kd=self.D
     dt=self.dt
     der=(e-eant)/dt
# control signal     
     up=kp*e
     ui=ki*eint*dt 
#Anti-windup
     if ui > umax:
         ui = umax
     elif ui < umin:
         ui = umin
###############    
     ud=kd*der
     U = up+ui+ud

#Avoid saturation
     if U > umax:
         U = umax
     elif U < umin:
         U = umin
     return U , ui
     
   def update(e,eint):
       
       eant=e
       eint=eint+e
       return eant,eint
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       