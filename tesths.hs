{- Assignment 1
 - Name: Sunny Bhatt
 - Date: 2018-09-28
 -}
 module Assign_1 where

    macid :: String
    macid = "bhatts39"

    {- Take the cube root of x by raising it to the power of 1/3. The cube root of the absolute value of x is taken
       and then multiplied by -1 or +1 -}
    cubeRoot :: Double -> Double
    cubeRoot x 
        | x == 0 = 0
        | otherwise = (abs x)**(1/3) * (x/(abs x))

    {- Calculate Q from a b and of a cubic function -}
    cubicQ :: Double -> Double -> Double -> Double
    cubicQ a b c = (3*a*c - b^2)/(9*a^2)
    
    {- Calculate R from a b c and d of a cubic function -}
    cubicR :: Double -> Double -> Double -> Double -> Double
    cubicR a b c d = (9*a*b*c - 27*(a^2)*d - 2*b^3) / (54*a^3)
    
    {- Calculate the discriminant of a cubic function -}
    cubicDisc :: Double -> Double -> Double
    cubicDisc q r = (q^3) + (r^2)
    
    {- Calculate the cubicS using the discriminant -}
    cubicS :: Double -> Double -> Double
    cubicS q r = 
        cubeRoot (r + sqrt(disc))
        where disc = cubicDisc q r
    
    {- Calculate the cubicT using the discriminant -}
    cubicT :: Double -> Double -> Double
    cubicT q r = 
        cubeRoot (r - sqrt(disc))
        where disc = cubicDisc q r
    
    {- Check the value of the discriminant and return cubic roots accordingly -}
    cubicRealSolutions :: Double -> Double -> Double -> Double -> [Double]
    cubicRealSolutions a b c d 
        | abs(disc) < 1e-8 = [x1,x2,x2]
        | (disc > 0) = [x1]
        | otherwise =  [] 
        where
        disc = cubicDisc q r
        q = cubicQ a b c 
        r = cubicR a b c d
        s = cubicS q r
        t = cubicT q r
        x1 = (s + t) - (b/(3*a))
        x2 = -((s + t)/2) - (b/(3*a))
