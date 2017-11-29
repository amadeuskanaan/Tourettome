%% clearallcloseall
% ------------------------
clear all
close all


%% load toolboxes and define paths
% ------------------------
for pathtoolbox = 1

    % you need to change the P variable to your path
    % and these paths too relative to where your data are
    %addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software/surfstat_chicago')
    %addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software')
    
    addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software/surfstat_chicago')
    addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software')
    
    %P               = '/Users/kanaan/SCR/workspace/project_touretome/FSDIR/';
    P               = '/Users/kanaan/SCR/workspace/project_touretome/FSDIR/';
    RPATH           = [P '/Results_CT_BGcov'];
    mkdir(RPATH);

    phenotypic = '/Users/kanaan/SCR/workspace/project_touretome/phenotypic/phenotypic_tourettome.csv'

end

ice = textread('ice.m');

%% read fs average stuff (surfaces, parcellations, curvature)
% ------------------------
for readsurfdata = 1

    cd([P 'surf_fsa5'])
    SPHERE = SurfStatReadSurf({'lh.sphere','rh.sphere'});
    S = SurfStatReadSurf({'lh.inflated','rh.inflated'});
    SW = SurfStatReadSurf({'lh.white','rh.white'});
    SP = SurfStatReadSurf({'lh.pial','rh.pial'});
    SM.tri = SW.tri;
    SM.coord = (SW.coord + SP.coord)./2;

    SInf = SW;
    SInf.coord = 0.2 *SW.coord + 0.8* S.coord;


    CURV = SurfStatReadData({['fsaverage_curv_lh.asc'],['fsaverage_curv_rh.asc']});

    %f = figure;
    %    BoSurfStatViewData(sign(CURV),SM,'');
    %    colormap([0.6 0.6 0.6; 0.8 0.8 0.8]);
    %    exportfigbo(f,[RPATH 'fsaverage.png'],'png',10);
    %close(f)


end


%% read Tourettome csv phenotypic info
% ------------------------
for readcsv = 1
    
    cd(P)
    fid = fopen(phenotypic); % final group
    
    % ID ,Group,Site,Age,Sex,  %s%s%s%f%s
    % R_Caud,L_Caud,R_Puta,L_Puta,R_Pall,L_Pall, %f%f%f%f%f%f
    % R_Amyg,L_Amyg,R_Hipp,L_Hipp,R_Accu,L_Accu, %f%f%f%f%f%f
    % R_Thal,L_Thal, %f%f
    % Caud,Puta,Pall,Amyg,Hipp,Accu,Thal %f%f%f%f%f%f%f
       
    C   = textscan(fid,'%s%s%s%f%s%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f%f','Delimiter',',','headerLines',1,'CollectOutput',1);
    fclose(fid);
    
    % These are the variables of interest 
    % -- % ID ,Group,Site,Age,Sex, 

    ID         = C{1}(:,1);
    GROUP      = C{1}(:,2);
    SITE       = C{1}(:,3);
    AGE        = C{2};
    SEX        = C{3};
    BG.R_CAUD     = C{4}(:,1);
    BG.L_CAUD     = C{4}(:,2);
    BG.R_PUTA     = C{4}(:,3);
    BG.L_PUTA     = C{4}(:,4);
    BG.R_PALL     = C{4}(:,5);
    BG.L_PALL     = C{4}(:,6);
    %BG.R_AMYG     = C{4}(:,7);
    %BG.L_AMYG     = C{4}(:,8);
    %BG.R_HIPP     = C{4}(:,9);
    %BG.L_HIPP     = C{4}(:,10);
    %BG.R_ACCU     = C{4}(:,11);
    %BG.L_ACCU     = C{4}(:,12);
    BG.R_THAL     = C{4}(:,13);
    BG.L_THAL     = C{4}(:,14);
    BG.CAUD       = C{4}(:,15);
    BG.PUTA       = C{4}(:,16);
    BG.PALL       = C{4}(:,17);
    %BG.AMYG       = C{4}(:,18);
    %BG.HIPP       = C{4}(:,19);
    %BG.ACCU       = C{4}(:,20);
    BG.THAL       = C{4}(:,21);
    BG.L_STR      = BG.L_PUTA + BG.L_CAUD %+ BG.L_ACCU;
    BG.R_STR      = BG.R_PUTA + BG.R_CAUD %+ BG.R_ACCU;
    BG.L_BG       = BG.L_STR + BG.L_PALL;
    BG.R_BG       = BG.R_STR + BG.R_PALL;
    
end


%% Read the thickness data 
% ------------------------
for loadct = 1
    
   cd([P 'FS_CT'])
   T20      = zeros(length(ID),size(SW.coord,2));
   myleft   = strcat(ID,'_lh2fsaverage5_20.mgh');
   myright  = strcat(ID,'_rh2fsaverage5_20.mgh');
   keep = ones(length(ID),1); 
   for i = 1:length(ID)
       try
           left      = SurfStatReadData1(myleft{i}); 
           right      = SurfStatReadData1(myright{i}); 
           T20(i,:)       = [left, right];

       catch
           keep(i) = 0; 
           disp(ID{i}) 
       end
   end
end  

keep        = find(keep); 
IDk         = ID(keep);
SITEk       = SITE(keep); 
GROUPk      = GROUP(keep);  
AGEk        = AGE(keep); 
SEXk        = SEX(keep); 
T20k        = T20(keep,:); 

%T20k_fname = fullfile(RPATH, 'T20k_table.csv')
%dlmwrite(T20k, T20k);

T20arrt = array2table(T20k);
T20k_fname = fullfile(RPATH, 'T20k_table.csv')
T20_table = table(IDk,GROUPk, SITEk, T20k)
%writetable(T20_table ,T20k_fname)

%% generate the mask using heuristic approach
% ------------------------
mask  = mean(T20k,1) > 0.4;

%% clusp setting across all analyses
% ------------------------
clusp = 0.025; 


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Figure 3 analyses: Covariance between BG volumes and Cortical Thickness

% here BG cols have to be claculated in native space, as freesurfer data is
for covariance = 1 
    
  bg = fieldnames(BG) 
  
  for b = 1:length(bg) 
        
    if bg{b}(1) == 'R'
        bg_name = [bg{b}(3:end) '_R'];
    elseif bg{b}(1) == 'L'
        bg_name = [bg{b}(3:end) '_L'];
    else
        bg_name = bg{b};
    end 

    disp([' --------- ' bg_name ' ----------']) 
    seed = getfield(BG, bg{b}); 
    seedk = seed(keep);

    % make terms needed for the modeling
    Seed  = term(seedk);
    G     = term(GROUPk);
    SI    = term(SITEk);
    A     = term(AGEk);
    SE    = term(SEXk);

    %%%%%%%%%%%%%%%%%%%
    % Linear model
    M     = 1 + SI + G + Seed + G*Seed ;
    slm   = SurfStatLinMod(T20k,M,SW);
    slm   = SurfStatT(slm,(G.controls.*seedk)-(G.patients.*seedk) );

    %f=figure, BoSurfStatViewData(slm.t,SM,[bg{b} ' T-stat(FWE) controls>patients'])
    %    SurfStatColLim([-5 5])
    %    exportfigbo(f, [RPATH '/' bg_name '_covariance_C>P_t.png'],'png',10)
    %close(f)

    % multiple comparison correction (controls > patients)
    [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 

    effect = slm.t;
    if isfield(pval,'C')
        effect(pval.C>0.025) = 0;
        %effect(pval.C<0.025) = 1;
        %dlmwrite([RPATH '/' bg{b} '_thickness_mask_cp.csv'], effect);

        f=figure,
            BoSurfStatViewData(effect, SM, [bg_name 'Tstat(FWE) C>P'])
            SurfStatColLim([2 5])
            colormap([0.8 .8 .8; ice/255])
            exportfigbo(f, [RPATH '/' bg_name '_covariance_C>P_fwe.png'],'png',10)
        close(f)
    end

    % multiple comparison correction (controls < patients)
    slm.t = -slm.t
    [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 
    effect = slm.t; 
    if isfield(pval,'C')
        effect(pval.C>0.025) = 0;
        %effect(pval.C<0.025) = 1;
        %dlmwrite([RPATH '/' bg{b} '_thickness_mask_pc.csv'], effect);

        f=figure,
            BoSurfStatViewData(effect, SM, [bg_name ' Tstat(FWE) C<P'])
            SurfStatColLim([2 5])
            colormap([0.8 .8 .8; hot])
            exportfigbo(f, [RPATH '/' bg_name '_covariance_C<P_fwe.png'],'png',10)
        close(f)
    end
  end
end   

