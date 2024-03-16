#include <cmath>
#include <iostream>
#include <fstream>
#include <cstdlib>
using namespace std;

double computeHauteurChuteNette(double debit_turbine, 
                                double debit_total, 
                                double niveau_amont) {
  double elevation_avale = -1.453 * pow(10,-6) * debit_total * debit_total \
    + 0.007022 * debit_total + 99.9812;

  double chute_nette = niveau_amont - elevation_avale \
    - (0.5 * (pow(10, -5)) * (debit_turbine * debit_turbine));
  
  return chute_nette;
}

double computePuissance(double coefficients[8], 
                        double debit_turbine, 
                        double chute_nette) {
  return coefficients[0] \
         + coefficients[1] * debit_turbine \
         + coefficients[2] * chute_nette \
         + coefficients[3] * pow(debit_turbine, 2) \
         + coefficients[4] * debit_turbine * chute_nette \
         + coefficients[5] * pow(chute_nette, 2) \
         + coefficients[6] * pow(debit_turbine, 3) \
         + coefficients[7] * pow(debit_turbine, 2)*chute_nette;
}

int main ( int argc , char ** argv ) {
  //Input params
  double debit_total;
  double niveau_amont;

  // Goal
  double f = -1e20;
  // constraints
  double debits[5] = {-1e20, -1e20, -1e20, -1e20, -1e20};
  double sum_debits = 0.0;
  
  // Coefficients
  double puissance_turbine_1[8] = {1.1018, -0.04866, -0.03187, 0.002182, 
                       0.003308, 0, -1.2771e-05, 3.683e-05};

  double puissance_turbine_2[8] = {0.6987, -0.175, -0.02011, 0.003632, 
                       0.004154, 0, -1.6988e-05, 3.5401e-05};
  double puissance_turbine_3[8] = {0.7799,  0.1995 , -0.02261, -3.519e-05 , 
                       -0.001695, 0, -9.338e-06, 7.235e-05};
  double puissance_turbine_4[8] = {20.2212 , -0.4586, -0.5777, 0.004886, 
                       0.01151, 0, -1.882e-05,   1.379e-05};
  double puissance_turbine_5[8] = {1.9786, 0.004009, -0.05699, 0.001064, 
                       0.005456, 0,  -8.162e-06,   2.849e-05};
  double* puissances_turbines[5] = {puissance_turbine_1, puissance_turbine_2, puissance_turbine_3, puissance_turbine_4, puissance_turbine_5};

  if ( argc >= 4 ) {
    // Get parameters
    debit_total = atof(argv[2]);
    niveau_amont = atof(argv[3]);

    ifstream in ( argv[1] );
    double ttl = 0;
    for ( int i = 0 ; i < 5 ; i++ ) {
      in >> debits[i];
      double hauteur_chute_nette = computeHauteurChuteNette(debits[i], debit_total, niveau_amont);
      double current_puissance = computePuissance(puissances_turbines[i], debits[i], hauteur_chute_nette);
      ttl += current_puissance;
      sum_debits += debits[i];
    }
    f = ttl;
    if ( in.fail() )
      f = sum_debits = -1e20;
    else {
      if (sum_debits > debit_total) {
        f = sum_debits = -1e20;
      }
    }
    in.close();
  }
  cout << f << " " << sum_debits << endl;
  return 0;
}
