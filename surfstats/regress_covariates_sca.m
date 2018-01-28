%plot

function [residuals] = regress_covariates_sca(tourettome_dir, feature_name, freesurfer_dir, phenotypic);


%% Function to regress covariates for feature data
% feature data can be CT or SCA mgh files
% reading feature data dependes on the number of subjects in the input phenotypic file
%
% Inputs arguments
%    derivatives_dir  : path to folder where feature data is located. Depending on feature, ie. CT or SCA,
%                       the correct folder are found
%    freesurfer_dir   : path to freesurfer_dir. Will look for fsaverage5 data here
%    phenotypic_csv   : path to phenotypic file with subject_ids and covariates to be regressed only


%% Input/Output
features_dir    = [tourettome_dir, '/derivatives/' feature_name, '/'];
out_dir         = [tourettome_dir, '/derivatives/feature_matrices/' ];
fsaverage5_dir  = '/scr/malta1/Github/Tourettome/algorithms/surfstats/fsaverage5/';

%%% define toolbox dirs
addpath('/scr/malta1/Github/Tourettome/algorithms/surfstats/software/surfstat_chicago')
addpath('/scr/malta1/Github/Tourettome/algorithms/npy_matlab')

% blue cmap
ice = textread('ice.m');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Define freesurfer data
surf_sphere = SurfStatReadSurf({[fsaverage5_dir 'lh.sphere'],[fsaverage5_dir 'rh.sphere']});
surf_curv   = SurfStatReadData({[fsaverage5_dir 'fsaverage_curv_lh.asc'],[fsaverage5_dir 'fsaverage_curv_rh.asc']});
surf_infl   = SurfStatReadSurf({[fsaverage5_dir 'lh.inflated'],[fsaverage5_dir 'rh.inflated']});
surf_white  = SurfStatReadSurf({[fsaverage5_dir 'lh.white'],[fsaverage5_dir 'rh.white']});
surf_pial   = SurfStatReadSurf({[fsaverage5_dir 'lh.pial'],[fsaverage5_dir 'rh.pial']});

surf_mid_ct.tri   = surf_white.tri;
surf_mid_ct.coord = (surf_white.coord + surf_white.coord)./2;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Read phenotypic data
phenotypic_fid  = fopen(phenotypic);
phenotypic_data = textscan(phenotypic_fid,'%s%f%s%s%s%f','Delimiter',',','headerLines',1,'CollectOutput',1);
fclose(phenotypic_fid);

phenotypic_id         = phenotypic_data{1};
phenotypic_age        = phenotypic_data{2};
phenotypic_group      = phenotypic_data{3}(:,1);
phenotypic_sex        = phenotypic_data{3}(:,2);
phenotypic_site       = phenotypic_data{3}(:,3);
phenotypic_fd         = phenotypic_data{4};


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% load feature data

strM_lh = strcat(features_dir, 'STR3_MOTOR/', phenotypic_id, '_sca_z_fwhm6_lh.npy');
strM_rh = strcat(features_dir, 'STR3_MOTOR/', phenotypic_id, '_sca_z_fwhm6_rh.npy');
strL_lh = strcat(features_dir, 'STR3_LIMBIC/', phenotypic_id, '_sca_z_fwhm6_lh.npy');
strL_rh = strcat(features_dir, 'STR3_LIMBIC/', phenotypic_id, '_sca_z_fwhm6_rh.npy');
strE_lh = strcat(features_dir, 'STR3_EXEC/', phenotypic_id, '_sca_z_fwhm6_lh.npy');
strE_rh = strcat(features_dir, 'STR3_EXEC/', phenotypic_id, '_sca_z_fwhm6_rh.npy');
% load all subject data into a matrix

MOTOR  = zeros(length(phenotypic_id),size(surf_white.coord,2));
for i = 1:length(phenotypic_id)
    try
       lh      = transpose(readNPY(strM_lh{i}));
       rh      = transpose(readNPY(strM_rh{i}));
       MOTOR(i,:)  = [lh, rh];
    end
end

LIMBIC  = zeros(length(phenotypic_id),size(surf_white.coord,2));
for i = 1:length(phenotypic_id)
    try
       lh      = transpose(readNPY(strL_lh{i}));
       rh      = transpose(readNPY(strL_rh{i}));
       LIMBIC(i,:)  = [lh, rh];
    end
end

EXEC  = zeros(length(phenotypic_id),size(surf_white.coord,2));
for i = 1:length(phenotypic_id)
    try
       lh      = transpose(readNPY(strE_lh{i}));
       rh      = transpose(readNPY(strE_rh{i}));
       EXEC(i,:)  = [lh, rh];
    end
end

features = horzcat(MOTOR, LIMBIC, EXEC);


% plot and save
dlmwrite([out_dir, 'tourettome_sca_raw.csv'], features);
fig=figure, imagesc(features,[-1,1]);
colormap('parula');
saveas(fig,[out_dir, 'tourettome_sca_raw.png']);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Build statistical model
% code variables of interest as terms
term_age    = term(phenotypic_age);
term_group  = term(phenotypic_group);
term_sex    = term(phenotypic_sex);
term_site   = term(phenotypic_site);
term_fd     = term(phenotypic_fd);

% buid linear model controlled for site, group, age, sex
df_model  = 1 + term_age + term_sex + term_site + term_fd;

% Estimaste model parameters
stat_model      = SurfStatLinMod(features,df_model,surf_white);

% save residuals
residuals = features - stat_model.X*stat_model.coef;

% plot and save
dlmwrite([out_dir, 'tourettome_sca_resid.csv'], residuals);
fig=figure, imagesc(residuals,[-1,1]);
colormap('parula');
saveas(fig,[out_dir, 'tourettome_sca_resid.png']);

