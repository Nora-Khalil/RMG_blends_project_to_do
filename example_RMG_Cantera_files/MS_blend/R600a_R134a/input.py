
thermolibs = [
'NCSU_2025_revised',
'C1_C2_Fluorine',
'PFCA_thermo',
'primaryThermoLibrary',
'FFCM1(-)',
'halogens',
'CHOF_G4',
'CHOCl_G4',
'CHOBr_G4',
'CHOFCl_G4',
'CHOFBr_G4',
'CHOFClBr_G4',
'DFT_QCI_thermo',
'Fluorine',
'2-BTP_G4',
'thermo_DFT_CCSDTF12_BAC',
'SulfurHaynes',
]


database(
thermoLibraries = thermolibs,
reactionLibraries = ['FFCM1(-)', "ANL_Brown_pdep", "ANL_Brown_pdep_2", 'Brown_difluoromethane_seed', 'halogens_pdep'],    
seedMechanisms = [],
kineticsDepositories = ['training'],
kineticsFamilies = ['default','halogens', "PFAS", 'Disproportionation-Y'],
frequenciesLibraries = ['halogens_G4'],
kineticsEstimator = 'rate rules',
)

species(
    label = 'R600a',
    reactive = True,
    structure = SMILES('CC(C)C')
)


species(
    label = 'R134a',
    reactive = True,
    structure = SMILES('C(C(F)(F)F)F')
)


species(
    label = 'O2',
    reactive = True,
    structure = SMILES('[O][O]')
)


species(
    label = 'N2',
    reactive = False,
    structure = SMILES('N#N')
)

species(
    label = 'CO2',
    reactive = True,
    structure = SMILES('O=C=O')
)


simulator(
    atol = 1e-16,
    rtol = 1e-08,
    sens_atol = 1e-06,
    sens_rtol = 0.0001,
)


generatedSpeciesConstraints(
    allowed=['input species','seed mechanisms','reaction libraries'],
    maximumCarbonAtoms=8,
    maximumOxygenAtoms=6,
    #maximumHeavyAtoms=24,
    maximumRadicalElectrons=2,
    maximumSingletCarbenes=1,
    maximumCarbeneRadicals=0,
    allowSingletO2 = True,
)

options(
    units = "si",
    generateSeedEachIteration = True,
    generateOutputHTML = False,
    generatePlots = False,
    saveSimulationProfiles = False,
    saveEdgeSpecies = True,
    keepIrreversible = True,
    verboseComments = False,
)

simpleReactor(
        temperature=[(800,'K'),(2000,'K')],
        pressure= [(1.0,'bar'),(10.0,'bar')],
        nSims=10,
        initialMoleFractions={

        ##### stoichiometric combustion
        #normalized to oxygen: 0.125C4H10 + 0.125CH2F-CF3 + 1.0 O2 + 3.76 N2= 0.75 CO2 + 0.5 H2O + 0.5 HF
        #not normalized: 0.5C4H10 + 0.5CH2F-CF3 + 4.0 O2 + 15.04 N2= 3.0 CO2 + 2.0 H2O + 2.0 HF



        "R600a": [0.1, 0.15], #a little below and a little above stoich for a 50/50 binary blend
        "R134a": [0.1, 0.15],
        "O2": 1,
        "N2": 3.76,
        

        },
        #terminationRateRatio=1e-4,
        #terminationTime=(10,'s'),
        terminationTime=(2,'s'),
        #sensitivity=['halogen','OH'],
        #sensitivityThreshold=0.001,
        )



model(
    toleranceMoveToCore = 0.1,
    toleranceBranchReactionToCore=0.001, #using recommended values, which are said to be sufficient
    toleranceInterruptSimulation = 0.1,
    maximumEdgeSpecies = 3e5,
    filterReactions = True,
    filterThreshold = 5e8,
    minCoreSizeForPrune = 50,
    minSpeciesExistIterationsForPrune = 4,
    branchingIndex=0.5, #using recommended values,
    branchingRatioMax=1.0, #using recommended values,
)


pressureDependence(
    method='modified strong collision',
    maximumGrainSize=(0.5,'kcal/mol'),
    minimumNumberOfGrains=250,
    temperatures=(300,2500,'K',8),
    pressures=(0.01,100,'bar',5),
    interpolation=('Chebyshev', 6, 4),
    maximumAtoms=16,
    completedNetworks=['CH2O2', 'CO3'],
)
