# Used to generate data for "The labour and resource use requirements of a good life for all"
# Authors: Chris McElroy and Daniel W. O'Neill

import pymrio
import numpy as np
import pandas as pd
import spending as spending
import demographics as dem

# source folders
# TODO edit before running: repo_path = "path/to/exiobase/data/on/your/computer" + "/"
save_folder_name = "full data"
excel_folder_name = "excel output/" # this folder must exist in the source folder before it is saved to, and data there will be overwritten each time
concordance_name = "EXIOBASE20p_7sectors.txt" # this should exist as a file in the source folder, it's available from https://ntnu.app.box.com/v/EXIOBASEconcordances

def load_data():
	try:
		return pymrio.load_all(path=(repo_path + save_folder_name))
	except pymrio.core.fileio.ReadError:
		print('making new saved data')
		source_data = pymrio.parse_exiobase3(path=(repo_path + "original data"))
		data = source_data.calc_all()
		data.save_all(path=(repo_path + save_folder_name))
		return data

def remove_exports_and_changes_in_inventories_and_valuables(data:pymrio.IOSystem):
	new_data = data.copy()
	new_data.Y.loc[:,idx[:,'Changes in inventories']] = 0
	new_data.Y.loc[:,idx[:,'Changes in valuables']] = 0
	new_data.Y.loc[:,idx[:,'Exports: Total (fob)']] = 0 # already 0
	return new_data

def create_scenario(spending_allotments):
	new_Y = gdc_2019.Y.copy()
	new_Y.loc[:, ("GB", "Final consumption expenditure by households")] += new_Y.loc[:, ("GB", "Final consumption expenditure by government")] + new_Y.loc[:,("GB", "Final consumption expenditure by non-profit organisations serving households (NPISH)")]
	new_Y.loc[:, ("GB", "Final consumption expenditure by government")] = 0 # zero these out after adding them to household spending
	new_Y.loc[:, ("GB", "Final consumption expenditure by non-profit organisations serving households (NPISH)")] = 0
	new_Y.loc[:, ("GB", "Gross fixed capital formation")] *= spending_allotments["Gross fixed capital formation"]/(new_Y.loc[:, ("GB", "Gross fixed capital formation")].sum())
	adjust_spending(new_Y, spending_allotments)
	return new_Y

def adjust_spending(Y: pd.DataFrame, spending_allotments):
	for c in spending.categories:
		current_total = 0
		set_total = spending_allotments[c]

		# get total spending in all sectors in this category
		for sector in spending.sector_alignment[c]:
			current_total += Y.loc[idx[:, sector], ("GB", "Final consumption expenditure by households")].sum()

		# scale all sectoral spending within that category equally (skip if 0)
		if current_total == 0: continue
		scale = set_total / current_total
		for sector in spending.sector_alignment[c]:
			Y.loc[idx[:, sector], ("GB", "Final consumption expenditure by households")] *= scale

def labour_by_category():
	## NOTE that these categories were made for 2019 UK spending so other countries/years are not captured correctly,
	## because they include spending that is not included in the categorization

	breakdown_list = []
	for scenario in main_scenarios[4:]:
		# create a Yagg that has separate columns for each spending category
		Yagg = pd.DataFrame(scenario[1].loc[:, scenario[2]])
		Yagg = Yagg.groupby(by=['Direct spending','Direct spending','Direct spending','Gross fixed capital formation','Other','Other','Other'], axis=1, sort=False).sum()
		for c in spending.categories:
			if c == 'Gross fixed capital formation':
				# puts gfcf at the back of the list
				tempGFCF = Yagg.loc[:, c]
				Yagg.drop(c, axis=1, inplace=True)
				Yagg.loc[:, c] = tempGFCF
				continue
			if c == 'Not included': continue
			Yagg.loc[:, c] = Yagg.loc[:, 'Direct spending']
			for s in gdc_2019.get_sectors():
				if s not in spending.sector_alignment[c]:
					Yagg.loc[idx[:, s], c] = 0	
		Yagg.drop('Direct spending', axis=1, inplace=True)
		Yagg.drop('Other', axis=1, inplace=True)
		# ignores F_Y (irrelevant for employment hours)
		labour_by_category = pd.DataFrame(employment_hours_M @ Yagg)
		# adjust to hours per week equivalent (multiply by 1000000, divide by working age adults in 2019 and weeks per year)
		labour_by_category *= 1000000/(dem.total_population[scenario[3]]*dem.working_age_ratio[scenario[3]]*employment_during_working_age)/weeks_per_year
		# labour_by_category.name = scenario[0]
		labour_by_category.columns = [scenario[0]]
		breakdown_list.append(labour_by_category)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "labour_by_category.xlsx")

def labour_by_loc():
	breakdown_list = []
	# generate a version of S, and then M, broken out by regions
	S_diag = pd.DataFrame(np.diag(employment_hours_S), index=gdc_2019.L.index, columns=gdc_2019.L.index)
	S_reg = S_diag.groupby(level='region', axis=0, sort=False).sum()
	M_reg = S_reg @ gdc_2019.L
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			labour_by_loc = pd.Series([0, 0, (M_reg @ Yagg).sum().sum()], index=['Domestic', 'Imported', 'Total'], name=scenario[0])
		else:
			Yagg = Yagg.loc[:, scenario[2]]
			labour_by_region = M_reg @ Yagg
			labour_by_loc = pd.Series([labour_by_region.loc[scenario[2]], labour_by_region.sum() - labour_by_region.loc[scenario[2]], 0], index=['Domestic', 'Imported', 'Total'], name=scenario[0])
		# adjust to hours per week equivalent (multiply by 1000000, divide by working age adults in 2019 and weeks per year)
		labour_by_loc *= 1000000/(dem.total_population[scenario[3]]*dem.working_age_ratio[scenario[3]]*employment_during_working_age)/weeks_per_year
		breakdown_list.append(labour_by_loc)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "labour_by_loc.xlsx")

def labour_by_sector():
	breakdown_list = []
	# generate a version of S, and then M, broken out by sectors
	S_diag = pd.DataFrame(np.diag(employment_hours_S), index=gdc_2019.L.index, columns=gdc_2019.L.index)
	S_sec = S_diag.groupby(level='sector', axis=0, sort=False).sum()
	M_sec = S_sec @ gdc_2019.L
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			Yagg = Yagg.sum(axis=1)
		else:
			Yagg = Yagg.loc[:, scenario[2]]
		# ignores F_Y (irrelevant for employment hours) and converts to simple sectors
		labour_by_sector = (M_sec @ Yagg).T @ simple_sectors
		# adjust to hours per week equivalent (multiply by 1000000, divide by working age adults in 2019 and weeks per year)
		labour_by_sector *= 1000000/(dem.total_population[scenario[3]]*dem.working_age_ratio[scenario[3]]*employment_during_working_age)/weeks_per_year
		labour_by_sector.name = scenario[0]
		breakdown_list.append(labour_by_sector)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "labour_by_sector.xlsx")

def labour_by_skill():
	breakdown_list = []
	# generate a version of M broken out by skills
	M_skill_and_gender = gdc_2019.employment.M.loc['Employment hours: High-skilled female':'Employment hours: Medium-skilled male']
	M_skill = M_skill_and_gender.groupby(by=['High skill','High skill','Low skill','Low skill','Medium skill','Medium skill'], axis=0, sort=False).sum()
	# puts high skill at the back of the list
	tempHighSkill = M_skill.loc['High skill']
	M_skill.drop('High skill', axis=0, inplace=True)
	M_skill.loc['High skill'] = tempHighSkill
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			Yagg = Yagg.sum(axis=1)
		else:
			Yagg = Yagg.loc[:, scenario[2]]
		# ignores F_Y (irrelevant for employment hours)
		labour_by_skill = (M_skill @ Yagg).T
		# adjust to hours per week equivalent (multiply by 1000000, divide by working age adults in 2019 and weeks per year)
		labour_by_skill *= 1000000/(dem.total_population[scenario[3]]*dem.working_age_ratio[scenario[3]]*employment_during_working_age)/weeks_per_year
		labour_by_skill.name = scenario[0]
		# labour_by_skill.columns = [scenario[0]]
		breakdown_list.append(labour_by_skill)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "labour_by_skill.xlsx")

def energy_by_loc():
	breakdown_list = []
	# generate a version of S, and then M, broken out by regions
	S_diag = pd.DataFrame(np.diag(gdc_2019.energy.S.loc['Energy use - Final']), index=gdc_2019.L.index, columns=gdc_2019.L.index)
	S_reg = S_diag.groupby(level='region', axis=0, sort=False).sum()
	M_reg = S_reg @ gdc_2019.L
	# generate total direct energy by region
	F_Y_tot = gdc_2019.energy.F_Y.loc['Energy use - Final'].groupby(level='region', sort=False).sum()
	# calculate uk embodied energy for scaling scenarios
	uk_embodied_energy = (M_reg @ gdc_2019.Y.groupby(level='region', axis=1, sort=False).sum().loc[: , 'GB']).sum()
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			energy_by_loc = pd.Series([0, 0, (M_reg @ Yagg).sum().sum(), F_Y_tot.sum()], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		else:
			Yagg = Yagg.loc[:, scenario[2]]
			energy_by_region = M_reg @ Yagg
			F_Y = F_Y_tot.loc[scenario[2]]
			# scale direct energy in scenarios to match the difference in embodied energy
			if scenario[0].endswith('scenario'):
				F_Y *= energy_by_region.sum()/uk_embodied_energy
			energy_by_loc = pd.Series([energy_by_region.loc[scenario[2]], energy_by_region.sum() - energy_by_region.loc[scenario[2]], 0, F_Y], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		# adjust to per capita energy use (multiply by 1000 for GJ, divide by population in 2019)
		energy_by_loc *= 1000/(dem.total_population[scenario[3]])
		breakdown_list.append(energy_by_loc)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "energy_by_loc.xlsx")

def get_AR5_emissions(df):
	# made to match "GHG emissions AR5 (GWP100) | GWP100 (IPCC, 2010)" vector in EXIOBASE 3.8.2
	AR5_emissions = df.loc['As - combustion - air']*0.0
	co2_eq_factors = {
		'CH4 - combustion - air': 28,
		'CO2 - combustion - air': 1,
		'CO2_bio - combustion - air': 1,
		'N2O - combustion - air': 265,
		'CH4 - non combustion - Extraction/production of (natural) gas - air': 28,
		'CH4 - non combustion - Extraction/production of crude oil - air': 28,
		'CH4 - non combustion - Mining of antracite - air': 28,
		'CH4 - non combustion - Mining of bituminous coal - air': 28,
		'CH4 - non combustion - Mining of coking coal - air': 28,
		'CH4 - non combustion - Mining of lignite (brown coal) - air': 28,
		'CH4 - non combustion - Mining of sub-bituminous coal - air': 28,
		'CH4 - non combustion - Oil refinery - air': 28,
		'CO2 - non combustion - Cement production - air': 1,
		'CO2 - non combustion - Lime production - air': 1,
		'SF6 - air': 23500,
		'HFC - air': 1,
		'PFC - air': 1,
		'CH4 - agriculture - air': 28,
		'CO2 - agriculture - peat decay - air': 1,
		'N2O - agriculture - air': 265,
		'CH4 - waste - air': 28,
		'CO2 - waste - biogenic - air': 1,
		'CO2 - waste - fossil - air': 1,
	}

	for c in df.index:
		if c in co2_eq_factors:
			AR5_emissions += df.loc[c]*co2_eq_factors[c]

	return AR5_emissions

def emissions_by_loc():
	breakdown_list = []
	# generate a version of S, and then M, broken out by regions
	S_diag = pd.DataFrame(np.diag(get_AR5_emissions(df=gdc_2019.air_emissions.S)), index=gdc_2019.L.index, columns=gdc_2019.L.index)
	S_reg = S_diag.groupby(level='region', axis=0, sort=False).sum()
	M_reg = S_reg @ gdc_2019.L
	# generate total direct emissions by region
	F_Y_tot = get_AR5_emissions(df=gdc_2019.air_emissions.F_Y).groupby(level='region', sort=False).sum()
	# calculate uk embodied emissions for scaling scenarios
	uk_embodied_emissions = (M_reg @ gdc_2019.Y.groupby(level='region', axis=1, sort=False).sum().loc[: , 'GB']).sum()
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			emissions_by_loc = pd.Series([0, 0, (M_reg @ Yagg).sum().sum(), F_Y_tot.sum()], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		else:
			Yagg = Yagg.loc[:, scenario[2]]
			emissions_by_region = M_reg @ Yagg
			F_Y = F_Y_tot.loc[scenario[2]]
			# scale direct emissions in scenarios to match the difference in embodied emissions
			if scenario[0].endswith('scenario'):
				F_Y *= emissions_by_region.sum()/uk_embodied_emissions
			emissions_by_loc = pd.Series([emissions_by_region.loc[scenario[2]], emissions_by_region.sum() - emissions_by_region.loc[scenario[2]], 0, F_Y], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		# adjust to per capita emissions (divide by 1000 for Mg CO2 eq, divide by population in 2019)
		emissions_by_loc /= 1000*(dem.total_population[scenario[3]])
		breakdown_list.append(emissions_by_loc)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "emissions_by_loc.xlsx")

def extraction_by_loc():
	breakdown_list = []
	# generate a version of S, and then M, broken out by regions
	S_diag = pd.DataFrame(np.diag(gdc_2019.material.S.sum()), index=gdc_2019.L.index, columns=gdc_2019.L.index)
	S_reg = S_diag.groupby(level='region', axis=0, sort=False).sum()
	M_reg = S_reg @ gdc_2019.L
	# generate total direct extraction by region
	F_Y_tot = gdc_2019.material.F_Y.sum().groupby(level='region', sort=False).sum()
	# calculate uk embodied extraction for scaling scenarios
	uk_embodied_extraction = (M_reg @ gdc_2019.Y.groupby(level='region', axis=1, sort=False).sum().loc[: , 'GB']).sum()
	for scenario in main_scenarios:
		Yagg = scenario[1].groupby(level='region', axis=1, sort=False).sum()
		if scenario[2] == 'Global':
			extraction_by_loc = pd.Series([0, 0, (M_reg @ Yagg).sum().sum(), F_Y_tot.sum()], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		else:
			Yagg = Yagg.loc[:, scenario[2]]
			extraction_by_region = M_reg @ Yagg
			F_Y = F_Y_tot.loc[scenario[2]]
			# scale direct extraction in scenarios to match the difference in embodied extraction
			if scenario[0].endswith('scenario'):
				F_Y *= extraction_by_region.sum()/uk_embodied_extraction
			extraction_by_loc = pd.Series([extraction_by_region.loc[scenario[2]], extraction_by_region.sum() - extraction_by_region.loc[scenario[2]], 0, F_Y], index=['Domestic', 'Imported', 'Total', 'Direct use'], name=scenario[0])
		# adjust to per capita extraction (multiply by 1000 for tons, divide by population in 2019)
		extraction_by_loc *= 1000/(dem.total_population[scenario[3]])
		breakdown_list.append(extraction_by_loc)
	breakdown_data = pd.concat(breakdown_list, axis=1)
	breakdown_data.to_excel(repo_path + excel_folder_name + "materials_by_loc.xlsx")

def total_domestic_labour():
	breakdown_list = []
	for scenario in main_scenarios[1:5]:
		total_hours = employment_hours_F.loc[scenario[2]].sum()
		# adjust to hours per week equivalent (multiply by 1000000, divide by working age adults in 2019 and weeks per year)
		total_hours *= 1000000/(dem.total_population[scenario[3]]*dem.working_age_ratio[scenario[3]]*employment_during_working_age)/weeks_per_year
		breakdown_list.append(total_hours)
	breakdown_data = pd.DataFrame(breakdown_list, index=[item[0] for item in main_scenarios[1:5]])
	breakdown_data.to_excel(repo_path + excel_folder_name + "total_domestic_labour.xlsx")

# formatting
idx = pd.IndexSlice
pd.set_option("display.max_columns", 10)
pd.set_option("display.max_rows", 20)
pd.set_option("display.min_rows", 15)
pd.set_option("display.max_colwidth", 25)
pd.set_option("expand_frame_repr", False)
pd.set_option("display.width", 170)

# weeks per year number is exactly 365.2425 / 7
# weeks off per year from https://www.gov.uk/holiday-entitlement-rights
weeks_per_year = 52.1775 - 5.6
 # employment_during_working_age is calculated in two parts just to make it more clear
years_worked_per_person = 40
employment_during_working_age = years_worked_per_person/(65-15)

# main scenario data
gdp_2019 = load_data()
gdc_2019 = remove_exports_and_changes_in_inventories_and_valuables(gdp_2019) # this is what all scenarios use for data

good_life = create_scenario(spending.good_life_spending)
decent_living = create_scenario(spending.decent_living_spending)

main_scenarios = [
	# scenario name, spending, region, demographics
	['Global 2019', gdc_2019.Y, 'Global', 'Global'],
	['India 2019', gdc_2019.Y, 'IN', 'IN'],
	['China 2019', gdc_2019.Y, 'CN', 'CN'],
	['US 2019', gdc_2019.Y, 'US', 'US'],
	['UK 2019', gdc_2019.Y, 'GB', 'GB'],
	['Decent living scenario', decent_living, 'GB', 'scenario'],
	['Good life scenario', good_life, 'GB', 'scenario'],
]

# sector conversion
simple_sectors = pd.read_csv((repo_path + concordance_name), sep="\t", header=0, index_col=0)
simple_sectors.index = gdc_2019.get_sectors()

employment_hours_M = gdc_2019.employment.M.loc['Employment hours: High-skilled female':'Employment hours: Medium-skilled male'].sum()
employment_hours_S = gdc_2019.employment.S.loc['Employment hours: High-skilled female':'Employment hours: Medium-skilled male'].sum()
employment_hours_F = gdc_2019.employment.F.loc['Employment hours: High-skilled female':'Employment hours: Medium-skilled male'].sum()
labour_by_category()
labour_by_loc()
labour_by_sector()
labour_by_skill()
energy_by_loc()
emissions_by_loc()
extraction_by_loc()
total_domestic_labour()
