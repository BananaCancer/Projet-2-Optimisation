#include <cmath>
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdexcept>
using namespace std;

// g++ main.cpp -o main
// 

// const double DEBIT_TOTAL = 578.005676269531;
// const double NIVEAU_AMONT = 137.899993896484; 

// const double MIN_DEBIT = 0.0; // Débit minimal admissible
// const double MAX_DEBIT = 160.0; // Débit maximal admissible


const double COEFFICIENTS_ELEV_AVAL[3] = {-1.453e-06, 0.007022, 99.9812}; // Coefficients pour calculer l'élévation aval

//                                       |  p00   |    x    |    y    |     x^2   |    x*y   |y^2|    x^3    |    x^2*y  | 
const double COEFFICIENTS_TURBINE_1[8] = {1.10180, -0.04866, -0.03187, 0.00218200, 0.0033080, 0, -1.2771e-05, 3.6830e-05}; // TURBINE 1
const double COEFFICIENTS_TURBINE_2[8] = {0.69870, -0.17500, -0.02011, 0.00363200, 0.0041540, 0, -1.6988e-05, 3.5401e-05}; // TURBINE 2
const double COEFFICIENTS_TURBINE_3[8] = {0.77990,  0.19950, -0.02261, -3.519e-05, -0.001695, 0, -9.3380e-06, 7.2350e-05}; // TURBINE 3
const double COEFFICIENTS_TURBINE_4[8] = {20.2212, -0.45860, -0.57770, 0.00488600, 0.0115100, 0, -1.8820e-05, 1.3790e-05}; // TURBINE 4
const double COEFFICIENTS_TURBINE_5[8] = {1.97860, 0.004009, -0.05699, 0.00106400,0.00545600, 0, -8.1620e-06, 2.8490e-05}; // TURBINE 5


double getChuteNette(double debit_turbine, double NIVEAU_AMONT, double DEBIT_TOTAL) {
    // Déterminer l'élévation avale en fonction du débit total
    double elevation_avale = COEFFICIENTS_ELEV_AVAL[0] * pow(DEBIT_TOTAL, 2) +
                             COEFFICIENTS_ELEV_AVAL[1] * DEBIT_TOTAL +
                             COEFFICIENTS_ELEV_AVAL[2];

    // Calculer la chute nette
    double chute_nette = NIVEAU_AMONT - elevation_avale - (0.5 * pow(10, -5) * pow(debit_turbine, 2));

    return chute_nette;
}



double powerFunction(double debit_turbine, double chute_nette, const double* coefficients) {
    // Calcul de la puissance en utilisant les coefficients fournis
    return coefficients[0] +
           coefficients[1] * debit_turbine +
           coefficients[2] * chute_nette +
           coefficients[3] * pow(debit_turbine, 2) +
           coefficients[4] * debit_turbine * chute_nette +
           coefficients[5] * pow(chute_nette, 2) +
           coefficients[6] * pow(debit_turbine, 3) +
           coefficients[7] * pow(debit_turbine, 2) * chute_nette;
}



int main(int argc, char **argv) {

    double DEBIT_TOTAL = 578.005676269531; // valeur par défault
    double NIVEAU_AMONT = 137.899993896484;  // valeur par défault
    double test_debit = 0.0;

    double puissance_totale = 1e20;
    double x[5];
    double sum_debits = 1e20;
    if (argc == 4) {
        DEBIT_TOTAL = atof(argv[1]);
        NIVEAU_AMONT = atof(argv[2]);

        ifstream in(argv[3]);
        double ttl = 0.0;
        sum_debits = 0.0;
        for (int i = 0; i < 5; i++) {
            in >> x[i];
            double debit_turbine = x[i];
            sum_debits += debit_turbine;
            double chute_nette = getChuteNette(debit_turbine, NIVEAU_AMONT, DEBIT_TOTAL);
            // std::cout << "turbine " << i+1 << " : "<< debit_turbine << " m^3/s"<< std::endl;
            // std::cout << "chute nette : " << chute_nette << " m" << std::endl;
            const double* coefficients;
            switch (i) {
                case 0:
                    coefficients = COEFFICIENTS_TURBINE_1;
                    break;
                case 1:
                    coefficients = COEFFICIENTS_TURBINE_2;
                    break;
                case 2:
                    coefficients = COEFFICIENTS_TURBINE_3;
                    break;
                case 3:
                    coefficients = COEFFICIENTS_TURBINE_4;
                    break;
                case 4:
                    coefficients = COEFFICIENTS_TURBINE_5;
                    break;
                default:
                    break;
            }
            double puissance_turbine = powerFunction(debit_turbine, chute_nette, coefficients);
            // std::cout << "puissance : " << puissance_turbine << " MW" << std::endl;
            ttl += puissance_turbine;
        }
        puissance_totale = - ttl;
        if (in.fail()) {
            // cout << "FAIL" << endl;
            puissance_totale = sum_debits = 1e20;
        } else {
            if (sum_debits > DEBIT_TOTAL) {
                puissance_totale = sum_debits = 1e20;
            }
        }
        in.close();
    }
    // std::cout << "Puissance totale : " << puissance_totale << std::endl;
    std::cout << puissance_totale << " " << sum_debits << std::endl;
    return 0;
}