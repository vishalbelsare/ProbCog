package edu.tum.cs.bayesnets.relational.inference;

import edu.tum.cs.bayesnets.core.BeliefNetworkEx.SampledDistribution;

public class LikelihoodWeighting extends Sampler {
	GroundBLN gbln;
	
	public LikelihoodWeighting(GroundBLN gbln) {
		super(gbln.groundBN);
		this.gbln = gbln;
	}
	
	public SampledDistribution infer(String[] queries, int numSamples, int infoInterval) throws Exception {
		// create full evidence
		String[][] evidence = this.gbln.db.getEntriesAsArray();
		int[] evidenceDomainIndices = gbln.getFullEvidence(evidence);
	
		// sample
		edu.tum.cs.bayesnets.inference.LikelihoodWeighting lw = new edu.tum.cs.bayesnets.inference.LikelihoodWeighting(gbln.groundBN);
		this.dist = lw.infer(evidenceDomainIndices, numSamples, infoInterval);
		
		// determine query nodes and print their distributions
		printResults(queries);
		return dist;
	}
}