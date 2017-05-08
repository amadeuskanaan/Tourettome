%% clearallcloseall
% ------------------------
clear all
close all


%% load toolboxes and define paths
% ------------------------
for pathtoolbox = 1

    % you need to change the P variable to your path
    % and these paths too relative to where your data are
    addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software/surfstat_chicago')
    addpath('/Users/kanaan/SCR/Github/Tourettome/surf/software')
    
    %addpath('/host/yeatman/local_raid/kanaan/Software/surfstat_chicago')
    %addpath('/host/yeatman/local_raid/kanaan/Software')
   
    
    P               = '/Users/kanaan/SCR/workspace/project_touretome/FSDIR/';
    %P               = '/host/yeatman/local_raid/kanaan/workspace/Tourettome/';
    RPATH           = [P '/Results_RQ'];
    mkdir(RPATH);
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
    filename = '/Users/kanaan/SCR/workspace/project_touretome/phenotypic/phenotypic_leipzig_qsm2.csv'
    %filename = '/host/yeatman/local_raid/kanaan/workspace/Tourettome/phenotypic/phenotypic_leipzig_qsm2.csv' % final group

    C = readtable(filename,'Delimiter',',','ReadVariableNames',true);
    %fid = fopen(filename, 'r'); % final group

    %fgetl(fid) %reads line but does nothing with it
    %% ,Name,Group,Site,Age,Sex,
    %% R_Caud,L_Caud,R_Puta,L_Puta,R_Pall,L_Pall,R_Amyg,L_Amyg,
    %% R_Hipp,L_Hipp,R_Accu,L_Accu,R_Thal,L_Thal,
    %% Caud,Puta,Pall, Amyg,Hipp,Accu,Thal,
    %% L_RN,R_RN,L_STN,R_STN,L_SN,R_SN,L_DN,R_DN,
    %% SN,STN,RN,GPe,GPi,DN,MRS_STR

    
    %ID,Name,Group,Site,Age,Sex, %f%f%f%f%s%f
    %R_Caud,L_Caud,R_Puta,L_Puta,R_Pall,L_Pall, %s%s%s%s%s%s
    %R_Amyg,L_Amyg,R_Hipp,L_Hipp,R_Accu,L_Accu,R_Thal,L_Thal, %s%s%s%s%s%s%s%s
    %Caud,Puta,Pall,Amyg,Hipp,Accu,Thal, %s%s%s%s%s%s%s
    %L_RN,R_RN,L_STN,R_STN,L_SN,R_SN,L_DN,R_DN,SN,STN,RN,GPe,GPi,DN,MRS_STR %s%s%s%s%s%s%s%s%s%s%s%s%s%s%s
    %
    % %f%f%f%f%s%f%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s
    %

    %C   = textscan(fid,'%f%f%f%f%s%f%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s','Delimiter',',','HeaderLines',1,'CollectOutput',1);
    %fclose(fid);
    

    % These are the variables of interest
    % -- % ID ,Group,Site,Age,Sex,

    ID         = C.ID;
    NAME       = C.Name;
    GROUP      = C.Group;
    SITE       = C.Site;
    AGE        = C.Age;
    SEX        = C.Sex;
    BG.R_Caud  = C.R_Caud;
    BG.L_Caud  = C.L_Caud;
    BG.R_Puta  = C.R_Puta;
    BG.L_Puta  = C.L_Puta;
    BG.R_Pall  = C.R_Pall;
    BG.L_Pall  = C.L_Pall;
    BG.R_Amyg  = C.R_Amyg;
    BG.L_Amyg  = C.L_Amyg;
    %BG.R_Hipp  = C.R_Hipp;
    %BG.L_Hipp  = C.L_Hipp;
    BG.R_Accu  = C.R_Accu;
    BG.L_Accu  = C.L_Accu;
    BG.R_Thal  = C.R_Thal;
    BG.L_Thal  = C.L_Thal;
    BG.Caud   = C.Caud;
    BG.Puta   = C.Puta;
    BG.Pall   = C.Pall;
    BG.Amyg   = C.Amyg;
    BG.Hipp   = C.Hipp;
    BG.Accu   = C.Accu;
    BG.Thal   = C.Thal;
    BG.L_RN   = C.L_RN;
    BG.R_RN   = C.R_RN;
    BG.L_STN  = C.L_STN;
    BG.R_STN  = C.R_STN;
    BG.L_SN   = C.L_SN;
    BG.R_SN   = C.R_SN;
    BG.L_DN   = C.L_DN;
    BG.R_DN   = C.R_DN;
    BG.SN     = C.SN;
    BG.STN    = C.STN;
    BG.RN     = C.RN;
    BG.GPe    = C.GPe;
    BG.GPi    = C.GPi;
    BG.DN     = C.DN;
    BG.MRS_STR= C.MRS_STR;


end


%% Read the thickness data
% ------------------------
for loadct = 1

   cd([P 'FS_QSM'])
   T20      = zeros(length(ID),size(SW.coord,2));
   myleft   = strcat(NAME,'_',ID,'_lh_qsm_fsaverage5_20.mgh');
   myright  = strcat(NAME,'_',ID,'_rh_qsm_fsaverage5_20.mgh');
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
T20k = T20k + 1;

%% generate the mask using heuristic approach
% ------------------------
mask  = mean(T20k,1) > 0.;

%% clusp setting across all analyses
% ------------------------
clusp = 0.05;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
for covariance = 1 
    
  bg = fieldnames(BG) 
  
  for b = 1:length(bg) 
         
        disp([' --------- ' bg{b} ' ----------']) 
        seed = getfield(BG, bg{b}); 
        %seed  = getfield(BG, 'L_Puta'); 
        seedk = seed(keep);

        clusp  = 0.025;


        % make terms needed for the modeling
        Seed  = term(seedk);
        G     = term(GROUPk);
        SI    = term(SITEk);
        A     = term(AGEk);
        SE    = term(SEXk);
        
        
          % Linea model
          % controlled for site, age, iq
          % ---
          M        = 1 + G + Seed + G*Seed;
          slm      = SurfStatLinMod(T20k,M,SW);
          slm      = SurfStatT(slm,(G.controls.*seedk)-(G.patients.*seedk) );

        f=figure, BoSurfStatViewData(slm.t,SM,[bg{b} 'T-stat(FWE) controls>patients'])
            SurfStatColLim([-5 5])
            %exportfigbo(f, [RPATH '/' bg{b} '_covariance_C>P_t.png'],'png',10)
        close(f)

        % multiple comparison correction (controls > patients)
        [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 

        effect = slm.t;
        if isfield(pval,'C')
            effect(pval.C>0.025) = 0;
            effect(pval.C<0.025) = 1;
            %dlmwrite([RPATH '/' bg{b} '_thickness_mask_cp.csv'], effect);

            f=figure,
                BoSurfStatViewData(effect, SM, [bg{b} 'T-stat(FWE) controls>patients'])
                SurfStatColLim([2 5])
                colormap([0.8 .8 .8; ice/255])
            %    exportfigbo(f, [RPATH '/' bg{b} '_covariance_C>P_fwe.png'],'png',10)
            close(f)
        end

        % multiple comparison correction (controls < patients)
        slm.t = -slm.t
        [pval, peak, clus, clusid] = SurfStatP(slm, mask, clusp); 
        effect = slm.t; 
        if isfield(pval,'C')
            effect(pval.C>0.025) = 0;
            effect(pval.C<0.025) = 1;
            %dlmwrite([RPATH '/' bg{b} '_thickness_mask_pc.csv'], effect);

            f=figure,
                BoSurfStatViewData(effect, SM, [bg{b} 'T-stat(FWE) controls<patients'])
                SurfStatColLim([2 5])
                colormap([0.8 .8 .8; hot])
                %exportfigbo(f, [RPATH '/' bg{b} '_covariance_C<P_fwe.png'],'png',10)
            close(f)
        end

    end

end   
