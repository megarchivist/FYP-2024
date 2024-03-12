# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 12:26:43 2024

@author: Cerys Morley
"""
import math

# finds elastic critical axial buckling stress
def calcElasticCriticalAxialBucklingStress(E,C_x,r,t):
    # EN 1993-1-6 D.6
    sigma = 0.605*E*C_x*t/r;
    return sigma

# find critical buckling factor C_x
def calcC_x(omega,r,t):

    if omega < 1.7: # EN 1993-1-6 D.3
        # short length
        C_x = 1.36 - (1.83/omega) + (2.07/(omega**2)); # EN 1993-1-6 D.8

    elif omega < 1.43*r/t: # EN 1993-1-6 D.4
        # medium length
        C_x = 1; # EN 1993-1-6 D.7

    else:
        # long length
        C_x = 1;

    return C_x

# relative length of shell segment
def calcRelativeLength(L,r,t):
    # EN 1993-1-6 Equation D.1
    omega = L/math.sqrt(r*t);
    return omega

# relative slenderness of shell segment
def calcRelativeSlenderness(f_yk,sigma):
    # EN 1993-1-6 Equations 9.19, 9.20, 9.21

    lambda_bar = math.sqrt(f_yk/sigma);
    # if doing shear stress, input f_yk = f_yk/sqrt(3)

    return lambda_bar

# elastic-plastic buckling reduction factor
def calcBucklingReductionFactor(lambda_bar,lambda_bar0,chi_h,alpha,beta,eta):
    lambda_barp = calcLambdaBarP(alpha, beta);

    if lambda_bar <= lambda_bar0:
        chi = chi_h - (lambda_bar/lambda_bar0)*(chi_h-1); # EN 1993-1-6 9.22
    elif lambda_bar < lambda_barp:
        chi = 1 - beta*(((lambda_bar-lambda_bar0)/(lambda_barp-lambda_bar0))**eta); # EN 1993-1-6 9.23
    else:
        chi = alpha/(lambda_bar**2); # EN 1993-1-6 9.24

    return chi

# calculate imperfection amplitude
def calcImperfectionAmplitude(Q_x,r,t):
    # EN 1993-1-6 D.14
    dt = math.sqrt(r/t)/Q_x;
    return dt

# calculate axial elastic imperfection reduction factor
def calcAlpha_x(dt):
    # EN 1993-1-6 D.11, D.12, D.13
    alpha_x = 0.83/(1 + 2.2*(dt**0.75));
    return alpha_x

# calculate axial plastic range factor
def calcBeta_x(dt):
    # EN 1993-1-6 D.15
    beta_x = 1 - (0.75/(1 + 1.1*dt));
    return beta_x

# plastic limit relative slenderness
def calcLambdaBarP(alpha,beta):
    LP = math.sqrt(alpha/(1-beta)); # EN 1993-1-6 9.25
    return LP

# calculate interaction exponent eta_x0
def calcEta_x0(dt):
    eta_x0 = 1.35 - 0.1*dt; # EN 1993-1-6 D.16
    return eta_x0

# calculate plastic (?) interaction exponent eta_xp
def calcEta_xp(dt):
    eta_xp = 1/(0.45 + 0.72*dt); # EN 1993-1-6 D.17
    return eta_xp

# interaction exponent
def calcEta(lambda_bar,lambda_bar0,lambda_barp,eta_0,eta_p):
    # EN 1993-1-6 9.26
    eta = ( (lambda_bar*(eta_p - eta_0)) + (lambda_barp*eta_0) - (lambda_bar0*eta_p) )/(lambda_barp-lambda_bar0);
    return eta

# characteristic & design buckling stresses
def calcDesignBucklingStress(chi,f_yk,gamma_M1):
    # if doing shear stress, input f_yk = f_yk/sqrt(3)
    sigma_Rk = chi*f_yk; # EN 1993-1-6 9.27, 9.28, 9.29

    sigma_Rd = sigma_Rk/gamma_M1; # EN 1993-1-6 9.30, 9.31, 9.32

    return sigma_Rd

# check individual components do not exceed design values
def checkIndividualStresses(N_Ed,N_Rd):
    # gives binary true/false: "Does it exceed buckling stress?"
    check = N_Ed <= N_Rd # EN 1993-1-6 9.33, 9.34, 9.35

    utilisation = N_Ed*100/N_Rd; # percentage

    return check, utilisation

# check interactions between stress components
def checkStressInteractions(sigma_Ed,sigma_Rd,k_i,alpha_i):
    # EN 1993-1-6 9.5.3 (4)
    if sigma_Ed[0] < 0:
        # if sigma_x,Ed is tensile
        sigma_Ed[0] = 0;
    if sigma_Ed[1] < 0:
        # if sigma_th,Ed is tensile
        sigma_Ed[1] = 0;

    # gives binary True/False scalar
    # EN 1993-1-6 9.36
    check = ((sigma_Ed[0]/sigma_Rd[0])**k_i[0]) - alpha_i*(sigma_Ed[0]/sigma_Rd[0])*(sigma_Ed[1]/sigma_Rd[1]) + ((sigma_Ed[1]/sigma_Rd[1])**k_i[1]) + ((sigma_Ed[2]/sigma_Rd[2])**k_i[2]) <= 1.0;
    return check

# buckling interaction parameters
def calck_iAndalpha_i(chi):
    # chi is list of size (3,); x, th, xth order
    k_i = [];
    k_i.append(1.0 + chi[0]**2); # EN 1993-1-6 9.37
    k_i.append(1.0 + chi[1]**2); # EN 1993-1-6 9.38
    k_i.append(1.5 + 0.5*(chi[2]**2)); # EN 1993-1-6 9.39

    alpha_i = (chi[0]*chi[1])**2; # EN 1993-1-6 9.40

    return k_i, alpha_i

# check that strake doesn't buckle
# constants
f_yk = 355; # characteristic steel strength [N/mm2]
gamma_M1 = 1.1; # EN 1993-1-6 Table 4.2
E = 210e3; # Young's Modulus [N/mm2]

Q_x = {"Class A":40, "Class B":25, "Class C": 16}; # EN 1993-1-6 Table D.1
chi_xh = 1.10; # EN 1993-1-6 D.19
lambda_x0 = 0.10; # EN 1993-1-6 D.10


# # geometry import
# filename = "Sadowskietal2023-benchmarkgeometries.csv";
# strakeID = 107;
# L, r, t = geometry.findStrakeGeometry(filename, strakeID);

def findAxialBucklingStress(E,f_yk,Q_x,lambda_x0,chi_xh,L,r,t):
    omega = calcRelativeLength(L, r, t);

    C_x = calcC_x(omega, r, t);
    sigma_xRcr = calcElasticCriticalAxialBucklingStress(E, C_x,r,t);

    lambda_bar = calcRelativeSlenderness(f_yk, sigma_xRcr);

    dt = calcImperfectionAmplitude(Q_x["Class A"], r, t);
    alpha = calcAlpha_x(dt);
    beta = calcBeta_x(dt);

    eta_x0 = calcEta_x0(dt);
    eta_xp = calcEta_xp(dt);
    lambda_barp = calcLambdaBarP(alpha, beta);

    eta = calcEta(lambda_bar, lambda_x0, lambda_barp, eta_x0, eta_xp);
    chi = calcBucklingReductionFactor(lambda_bar, lambda_x0, chi_xh, alpha, beta, eta);

    sigma_xRd = calcDesignBucklingStress(chi, f_yk, gamma_M1);

    return sigma_xRd
