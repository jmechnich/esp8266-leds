import colorsys

def convert(buffer, worker):
	for i in range(0,len(buffer),3):
		r,g,b = (i, i+1, i+2)

		for w in worker:
			buffer[r], buffer[g], buffer[b] = w(buffer[r:r+3])

def quad(src):
	return [ x**2 for x in src]

def multiply(factors=(1,1,1)):
	def f(src):
		return [ x[0] * x[1] for x in zip(src,factors) ]
	return f

def toUnit(src):
	f = 1.0/255.0 
	m = multiply( (f,f,f) )
	return m(src)

def toByte(src):
	return [ int( min( x*255.0, 255 ) ) for x in src ]

def toHSV(src):
	return colorsys.rgb_to_hsv(src[0],src[1],src[2])

def toRGB(src):
	return colorsys.hsv_to_rgb(src[0],src[1],src[2])

def gamma(g):
	def f(src):
		return [ x**g for x in src ]
	return f

def toLinear(src):
	g = gamma(1.0/2.2)
	return g(src)

def toNonLinear(src):
	g = gamma(2.2)
	return g(src)

def clamp(lower,upper):
	def f(l):
	    return [ max(lower,min(upper,i)) for i in l ]
	return f