#PROTOCOL to create the model description file

#### The model description file accompanies every model that a data scientist
#### develops and wants to upload into the SMART platform. As its name implies, it 
#### contains the relevant information needed to build the model:
#### (unit steps, input features, training ranges, target variables, ...) 
#### The file containing the model description contains all the necessary 
#### information needed by the GA. Wrong information can cause:
1) failure of model upload
2) failure of getting a recommendation 
3) not trustable predictions from recommendation algorithm (i.e. Genetic 
Algorithm)

IMPORTANT: the model description file MUST end with .desc.yml, i.e. model_file
.desc.yml

The model description file contains the following fields:

    name: general name, i.e. Solu+Ref+Chroma IPM
    # this name will appear in the model window on the platform 
    # (it can encompass multiple models corresponding to different unit 
    steps, see below). In this example it refers to a process covering 
    solubilization, refolding and chromatography. Two models will be used: 
    one covering refolding+chromatography, and one solu+refolding. The two 
    models will be called in chain by the recommendation algorithmg (GA): 
    first ref-chroma to extract the ref and chroma inputs which maximise the 
    chroma output, then the solu-ref model to provide the solu constraints 
    which maximise the refolding output 
    considering the refolding inputs recommended in the previous step.
 
    description: some description
    # the description will appear on the platform, it should be as explicative as possible
    
    project: product A8
    # identificative name of the product, to distinguish it from others
  
    type: biopharma
    # expert domain field 
   
   The above general part is followed by one ore more (in case of chain) 
   models described in detail   
 
    models:
   below, the list of models: it can be only one model, or more than one in case the optimization requires calling more models in chain
  
 
     name: MODEL NAME. KEY identificative of the model. The ORDER of models 
     is important. The first model to be added in this mdoel descr file 
     will be the first model called in the recommendation chain
    
     description: some description files: 
      - model_some_file.ann
      - model_some_file.yml
   REQUISITES:
   1) All model related files (including scalers, transformers, ...) MUST 
   start with the string "model" to distinguish from other files. It is RECOMMENDED
    to 'wrap' the models with the wrapper contained in the smart-suit 
    package. This is particularly true for model files composed of multiple
     files (weights, transformers,...): they can be wrapped in one single 
     file which is easier to handle by the recommendation algorithm 
   2) For wrapped models, it must be in dump format, not pickle. In case of 
   wrapped models, only one dump file is enough.
   3) The model name is identificative of the model. A given model name is
   associated to a model type:
   
     modelType:
        
      name: type of the model (Can be ANN, GBM, GP,...) 
          
      abbrevation: abbreviation for the type of model. A given model 
      (identified by its MODEL NAME) has a UNIQUE model type abbreviation. 
      For example, a model named 'Ref-chroma model' which is of type 'ANN' 
      cannot be of another type, like 'GP'. The same abbreviation (like 'ANN') 
      can be used for different model names.
   
   NOTE: When uploading a new version of the model (with its description file),
   if the MODEL NAME did not change, the model 
   abbreviation MUST not be changed, the version in the 
   platform will be changed automatically. If one wants to have a separate 
   model uploaded (i.e. one with GP and one with ANN), then a new model name 
   will be needed. See examples below:
   
    model name = ref chroma first 
    model type abbreviation: ANN_WRAP
    --> upload OK
   
    model name = ref chroma first 
    model type abbreviation: GP_WRAP
    --> ERROR in upload! a model with the same name already exists but the 
    type is different
   
    model name = ref chroma Second 
    model type abbreviation: ANN_WRAP
    --> upload OK: I new model was uploaded with a different name
   
   
   
   SPECIFIC ABBREVIATIONS:
   1) Always capital letters, max 20 letters
   2) Models wrapped with Wrapper must contain WRAP or -W
   3) Mimo models must contain "MIMO" in the model type
   4) Use MIMO_GP_WRAP for the case of GP MIMO WRAP
   5) Use MIMO_ANN_EMB_WRAP for the case of ANN MIMO WRAP with Categ 
   embedding (ONLY valid for ref-chroma unit steps)
  
   ------
   
   Below: description of the model. For the covered unit steps, all the 
   input features used in the model and their ranges are described.
   
   IMPORTANT POINTS:
   1) Make sure that the number of input features and outputs in the model 
   description file corresponds to that used to train the model
   2) The order of the unit steps is important: the first unit step which is
    described is the last unit step which is associated to one or more 
    targets. For example, in the case of 
    solubilization+refolding+chromatography, the last unit step is chromatography and should be 
   described as first, together with its targets, in the model descr file.
   3) The targets and objectives are currently accepted only for the 
   final step. 
   
   

      description: model type description
          unit steps:
          name: chromatography
            params:
            training_ranges:
            - name: Elution1 Salt Conc
              description: short description 
              type: float
              # type can be {integer, float, string} or ARRAY in case of 
              # categorical variables
              unit: g/L
              min: 0.1
              max: 1.5
              # min and max represent the ranges for the training data provided
              operationalMin: 0.0
              operationalMax: 2.0
              # operationMin and Max represent the extended ranges where the
               model is allowed to search for an optimal recommendation. 
               Make sure that the model is reliable outside the training 
               ranges. If so, the operational range should then be discussed
               with the scientists. When not indicated it is assumed to be 
               the same as the training range.

              stepsize: 0.01
              # it represents the significant digits associated to a given input 
              variable, it will be used to visualize the recommendations. It
              is provided by the scientists
              
          name: refolding
          description: some description
          params:
            training_ranges:
              - name: ph
                description: some description
                type: float
                # type can be {integer, float, string} or ARRAY in case of 
                # categorical variables
                unit: none
                min: 6.5
                max: 8.1
                operationalMin: 5.0
                operationalMax: 9.0
                stepsize: 0.1
              - name: Additives
                description: Additives
                type: ARRAY
                unit:
                min:
                max:
                params:
    
                - name: CHAPS
                  description: CHAPS
                  type: float
                  unit:
                  min: 6
                  max: 20
                  stepsize: 0.1
                - name: CaCl.2
                  description: CaCl.2
                  type: float
                  unit:
                  min: 5
                  max: 15
                  stepsize: 0.1
                - name: Redox
                  description: Redox
                  type: ARRAY
                  unit:
                  min:
                  max:
                  params:
                  - name: 0:3 mM
                    description: 0:3 mM
                    type: NONE
                  - name: 3:0 mM
                    description: 3:0 mM
                    type: NONE
                  - name: 3:3 mM
                    description: 3:3 mM
                    type: NONE

          target_variable: (list of targets for the model. Only for the last
           unit step)
            - name: Concentration
              description: Concentration
              unit: g/L
              stepsize: 0.1
            - name: Yield
              description: Yield
              unit:
              stepsize: 1
           
          objectives: (for each target, we have the objectives used in the 
          recommendation)
            - target: Concentration
              description: Concentration
              unit:
              importance: high
   Importance can be set by the user, but the default value will be 
              (high, mid, low)
              
              direction: max
   This is the direction of optimization (minimization or 
              maximization), it can also be set by the user, the default value 
              will be max or min
            
            - target: Yield
              description: Yield
              unit:
              importance: high
              direction: max



    name: IPM  Solu-Ref (represents the second model in the chain, in this 
    case covering solubilization and refolding)
        description: IPM Solu-Ref
        link: IPM Solu-Ref

   PREREQUISITE for using this link attribute is that the model that is 
       used in a link should be uploaded BEFORE the uploading this 
       current model description file. 
       Also, the current model must have CONSISTENT NOMENCLATURE for the common
       training ranges/input features/targets as the linked one. For 
       example, it the linked model and the current one have in common some 
       input parameters (like refolding conditions), then their names should
        be the same.