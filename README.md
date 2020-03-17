# covid_emod_hintschoolclosure
Config-only collaboration space for IDM-EMOD based scenario using HINT for school closure.

This started with the Scenario/Tutorial here: https://github.com/InstituteforDiseaseModeling/EMOD/tree/master/Regression/Scenarios/HINT/02_SchoolClosure

The key feature being leveraged in this approach is documented here: https://www.idmod.org/docs/general/model-hint.html#hint-s-node-with-one-individual-property

The idea is that the population is divided up into relevant age buckets and the TransmissionMatrix is configured to define the quantitative epi structure between the age groups. If you can get the baseline calibrated to your satisfaction you can configure a social distancing intervention with the Transitions feature of HINT. E.g.  https://github.com/jonathanhhb/covid_emod_hintschoolclosure/blob/master/hint_schoolclosure_demographics.json#L16

A sample of the kind of results this produces: https://github.com/jonathanhhb/covid_emod_hintschoolclosure/issues/4.

More to follow.
