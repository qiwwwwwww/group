
class Score{
    
    //Score function calculated the number of normalised people energy usage should be expected for one household
    //given their number of people in the household, insulation in their household, window glazing state and area
    //of the household
    double score(int numofppl, int insulationlv, int glazinglevel, double area){
        
        //we got our data from MATLAB by comparing 5 sets of data
        //Approach: We first randomly choose 5 sets of data from the dataset
        //Then: plot their average against the insulationlv and plot a regression line on it
        //Then: plot their average against the window glazing status and plot a regression line again
        //Then: plot their average against the area/100 and plot regression line again.
        //Then we extract the coefficient of those regression line
        //We made use of those coefficient to simulate the distribution by Gaussian distribution
        //we made our standard to household of size 100m^2, using level 3 insulation and single glazing window
        
        //It was a really elementary approach and build of the algorithm but the result is
        //quite promising.
        
        //c0 is more of a seasonal factor here as we did not really consider the seasonal effect on our data
        //it is also our normalised coefficient
        double c0=1.103
        
        //we got it from our empirical result, it does make sense to us as the larger the area of the household,
        //we expect them to use more energy so their score should decrease
        double c1=-0.342
        
        //we got it from our empirical result, it also makes sense as as the insulationlv increase, we
        //expect the score increase too because they should not be using more energy compare with the same
        //family size household
        double c2=0.754
        
        //Make sense with similar reason above
        double c3=0.886
        
        //Gaussian distribution
        double v1=exp((c1*((area-100)/100)));
        double v2=exp((c2*(insulationlv-3)));
        double v3=exp((c3*(glazinglevel-1)));
        double sc=c0*(numofppl*v1*v2*v3);
        
        return sc;
        
    }
};
