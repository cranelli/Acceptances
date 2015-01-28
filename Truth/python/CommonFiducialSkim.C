const string origFileLoc = "/data/users/cranelli/HOL1Muon/Trees/Version_5_1/HOMuonTree.root";
const string origTreeLoc = "demo/ho_muon_tree";

double loose_barrel_eta=1.5; //Looser Cut than is used in the analysis

void CommonFiducialSkim() {
  // Example of Root macro to copy a subset of a Tree to a new Tree
   
  //gSystem->Load("$ROOTSYS/test/libEvent");

  //Get old file, old tree and set top branch address
  TFile *origFile = new TFile(origFileLoc.c_str());
  TTree *origTree = (TTree*)origFile->Get(origTreeLoc.c_str());
  //Event *event   = new Event();
  //origTree->SetBranchAddress("event",&event);
  vector<float>* L1Muon_Etas;
  origTree->SetBranchAddress("L1Muon_Etas", &L1Muon_Etas);
  origTree->SetBranchStatus("*",0); //Disables All Branches
  
  //Then enables only select branches
  origTree->SetBranchStatus("Generator_Weights",1);
  origTree->SetBranchStatus("L1Muon_Etas",1);
  origTree->SetBranchStatus("L1Muon_Phis",1);
  origTree->SetBranchStatus("L1Muon_Pts",1);
  origTree->SetBranchStatus("HOReco_Etas",1);
  origTree->SetBranchStatus("HOReco_Phis",1);
  origTree->SetBranchStatus("HOReco_Energies",1);
  origTree->SetBranchStatus("hltMu5PropToRPC1_Etas",1);
  origTree->SetBranchStatus("hltMu5PropToRPC1_Phis",1);
  origTree->SetBranchStatus("hltMu5PropToRPC1_Pts",1);
  //origTree->SetBranchStatus("fH",1);

  //Create a new file + a clone of old tree in new file
  TFile *skimFile = new TFile("/data/users/cranelli/HOL1Muon/Trees/"
			      "Version_5_1/Skim_HOMuonTreee_Test.root",
			      "RECREATE");
  TTree *skimTree = origTree->CloneTree(0);

  Long64_t nentries = origTree->GetEntries();
  for (Long64_t i=0;i<nentries; i++) {
    if(i%1000==0) std::cout << i << std::endl;
    origTree->GetEntry(i);
    // Select Only Events with a L1Muon inside the barrel.
    bool keepEvent = false;
    for(unsigned int l1MuonB_index = 0; l1MuonB_index < L1Muon_Etas->size(); l1MuonB_index++){
      if(fabs(L1Muon_Etas->at(l1MuonB_index)) < loose_barrel_eta) keepEvent = true;
    }  
    if (keepEvent) skimTree->Fill();
    L1Muon_Etas->clear();
  }

  skimTree->Print();
  skimFile->Write();
  //delete oldfile;
  //delete newfile;
}
