/*
 * Created on Aug 17, 2009
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package edu.tum.cs.srl.bayesnets.inference;

import java.util.Collection;

import edu.ksu.cis.bnj.ver3.core.BeliefNode;
import edu.tum.cs.bayesnets.core.BeliefNetworkEx;
import edu.tum.cs.bayesnets.inference.GibbsSampling;
import edu.tum.cs.bayesnets.inference.SATIS_BSampler;
import edu.tum.cs.bayesnets.inference.Sampler;
import edu.tum.cs.bayesnets.inference.WeightedSample;
import edu.tum.cs.logic.sat.SampleSAT;
import edu.tum.cs.srl.bayesnets.bln.GroundBLN;
import edu.tum.cs.srl.bayesnets.bln.coupling.VariableLogicCoupling;

/**
 * SAT-IS Extended (with hard constraints from CPDs) that, for every SAT-IS step, 
 * adds a number of Gibbs steps to explore the subspace given by the sample;
 * the samples are weighted the same as the original SAT-IS sample 
 * @author jain
 */
public class SATISExGibbs extends SATISEx {
	protected int gibbsSteps = 9;

	public SATISExGibbs(GroundBLN bln) throws Exception {
		super(bln);
		this.paramHandler.add("gibbsSteps", "setNumGibbsSteps");
	}
	
	public void setNumGibbsSteps(int n) {
		gibbsSteps = n;
	}
	
	@Override
	protected Sampler getSampler() throws Exception {
		initSATSampler();
		return new SATIS_BSampler_Gibbs(gbln.getGroundNetwork(), ss, gbln.getCoupling(), determinedVars);
	}	
	
	public class SATIS_BSampler_Gibbs extends SATIS_BSampler {

		public GibbsSampling gibbsSampler;
		
		public SATIS_BSampler_Gibbs(BeliefNetworkEx bn, SampleSAT sat, VariableLogicCoupling coupling, Collection<BeliefNode> determinedVars) {
			super(bn, sat, coupling, determinedVars);
			gibbsSampler = new GibbsSampling(gbln.getGroundNetwork());
		}
		
		public void onAddedSample(WeightedSample s) throws Exception {
			for(int i = 0; i < gibbsSteps; i++) {
				gibbsSampler.gibbsStep(this.evidenceDomainIndices, s);
				addSample(s);
				currentStep++;
			}
		}
	}

}
