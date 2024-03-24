#include <cmath>
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdexcept>
using namespace std;

// g++ main.cpp -o main


const double COEFFICIENTS_ELEV_AVAL[3] = {-1.453e-06, 0.007022, 99.9812}; // Coefficients pour calculer l'élévation aval

//                                       |  p00   |    x    |    y    |     x^2   |    x*y   |y^2|    x^3    |    x^2*y  | 
const double COEFFICIENTS_TURBINE_1[8] = {1.10180, -0.04866, -0.03187, 0.00218200, 0.0033080, 0, -1.2771e-05, 3.6830e-05}; // TURBINE 1
const double COEFFICIENTS_TURBINE_2[8] = {0.69870, -0.17500, -0.02011, 0.00363200, 0.0041540, 0, -1.6988e-05, 3.5401e-05}; // TURBINE 2
const double COEFFICIENTS_TURBINE_3[8] = {0.77990,  0.19950, -0.02261, -3.519e-05, -0.001695, 0, -9.3380e-06, 7.2350e-05}; // TURBINE 3
const double COEFFICIENTS_TURBINE_4[8] = {20.2212, -0.45860, -0.57770, 0.00488600, 0.0115100, 0, -1.8820e-05, 1.3790e-05}; // TURBINE 4
const double COEFFICIENTS_TURBINE_5[8] = {1.97860, 0.004009, -0.05699, 0.00106400,0.00545600, 0, -8.1620e-06, 2.8490e-05}; // TURBINE 5

const double* COEFFICIENTS_TURBINES[5] = {COEFFICIENTS_TURBINE_1,
COEFFICIENTS_TURBINE_2, COEFFICIENTS_TURBINE_3, COEFFICIENTS_TURBINE_4,
COEFFICIENTS_TURBINE_5};

/**
 * @brief Calcule la hauteur de chute nette en fonction du débit de la turbine, 
 * du débit total et du niveau amont
 * 
 * @param debit_turbine Le débit de la turbine
 * @param niveau_amont Le nivea amont de l'eau
 * @param debit_total Le débit total disponible
 * @return double La hauteur de chute nette pour la turbine
 */
double getChuteNette(double debit_turbine, double niveau_amont, double debit_total) {
    // Déterminer l'élévation avale en fonction du débit total
    double elevation_avale = COEFFICIENTS_ELEV_AVAL[0] * pow(debit_total, 2) +
                             COEFFICIENTS_ELEV_AVAL[1] * debit_total +
                             COEFFICIENTS_ELEV_AVAL[2];

    // Calculer la chute nette
    double chute_nette = niveau_amont - elevation_avale - (0.5 * pow(10, -5) * pow(debit_turbine, 2));

    return chute_nette;
}

/**
 * @brief Calcule la puissance générée par la turbine en utilisant les 
 * coefficients fournis
 * 
 * @param debit_turbine Débit de la turbine
 * @param chute_nette Hauteur de chute nette
 * @param coefficients Coefficients de la fonction de modélisation pour 
 * calculer la puissance.
 * @return double La puissance générée par la turbine
 */
double powerFunction(double debit_turbine, double chute_nette, const double* coefficients) {
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
    // Données input
    double debit_total;
    double niveau_amont;

    // Initialisation des variables de décisions
    double puissance_totale = 1e20;
    double sum_debits = 1e20;

    if (argc == 4) {
        // Récupération des données input
        debit_total = atof(argv[1]);
        niveau_amont = atof(argv[2]);

        // Boucle pour récupérer les débits par turbines et calculer la 
        // puissance associée
        ifstream in(argv[3]);
        double ttl = 0.0;
        sum_debits = 0.0;
        double debit_actuel;
        for (int i = 0; i < 5; i++) {
            in >> debit_actuel;
            sum_debits += debit_actuel;
            double chute_nette = getChuteNette(debit_actuel, niveau_amont, debit_total);
            double puissance_turbine = powerFunction(debit_actuel, chute_nette, COEFFICIENTS_TURBINES[i]);
            ttl += puissance_turbine;
        }

        //On met la puissance en valeur négative vu qu'on cherche à minimiser
        puissance_totale = - ttl;
        
        //On considère que l'optimisation a échoué si le fichier de paramètres 
        //n'a pas pu être lu ou si la somme des débits dépasse le débit total 
        //disponible
        if (in.fail()) {
            puissance_totale = sum_debits = 1e20;
        } else {
            if (sum_debits > debit_total) {
                puissance_totale = sum_debits = 1e20;
            }
        }
        in.close();
    }
    std::cout << puissance_totale << " " << sum_debits << std::endl;
    return 0;
}