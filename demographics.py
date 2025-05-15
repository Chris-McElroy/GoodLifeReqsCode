# Used to generate data for "The labour and resource use requirements of a good life for all"
# Authors: Chris McElroy and Daniel W. O'Neill

# from https://data.oecd.org/pop/population.htm
# scenario number total people in households from https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/familiesandhouseholdsfamiliesandhouseholds/current
# for consistency with how the scenarios were generated
total_population = {
	'GB': 66796807,
	'US': 328329953,
	'ZA': 58532857,
	'IN': 1383112051,
	'BR': 210147125,
	'CN': 1421864034,
	'JP': 126555078,
	'DE': 83092956,
	'FR': 67349922,
	'CA': 37601230,
	'Global': 7764951032,
	'scenario': 65972000,
}

# from https://data.oecd.org/pop/working-age-population.htm
working_age_ratio = {
	'GB': 0.63567,
	'US': 0.65081,
	'ZA': 0.65338,
	'IN': 0.66934,
	'BR': 0.69377,
	'CN': 0.69716,
	'JP': 0.59691,
	'DE': 0.64704,
	'FR': 0.61883,
	'CA': 0.66471,
	'Global': 0.64921,
	'scenario': 0.63567,
}