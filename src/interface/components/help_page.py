"""
Help page component for the Streamlit interface.
"""

import streamlit as st


class HelpPage:
    """
    Help page with documentation and tutorials.
    """

    @staticmethod
    def render():
        """
        Render the help page.
        """
        st.title("Help & Documentation")

        st.markdown(
            """
        ## Getting Started
        
        This reliability analysis tool helps you analyze system reliability by:
        
        1. Building a system model
        2. Finding minimal cut sets
        3. Calculating system unreliability
        4. Running Monte Carlo simulations
        
        ### System Builder
        
        Use the System Builder to create your reliability system:
        
        - Add components with failure rates
        - Create connections between components
        - Use templates for common system types
        
        ### Cut Set Analysis
        
        The Cut Set Analysis page allows you to:
        
        - Find minimal cut sets using different algorithms
        - Compare algorithm performance
        - Visualize the minimal cut sets on your system
        - Generate unreliability expressions
        
        ### Simulation Analysis
        
        The Simulation Analysis page offers:
        
        - Monte Carlo simulation of system reliability
        - Statistical analysis of reliability metrics
        - Reliability plots with confidence intervals
        - Comparison with analytical solutions
        """
        )

        with st.expander("Theoretical Background"):
            st.markdown(
                """
            ### Reliability Theory
            
            **Minimal Cut Sets**: A cut set is a set of components that, when failed, causes the system to fail. A minimal cut set is a cut set that cannot be reduced further while still causing system failure.
            
            **Reliability Function**: The reliability of a system at time t is the probability that the system will function properly during the time interval [0, t].
            
            **Unreliability**: The unreliability (or failure probability) is the complement of reliability: F(t) = 1 - R(t).
            
            **Monte Carlo Simulation**: A statistical method that uses random sampling to obtain numerical results and estimate reliability metrics.
            """
            )

        with st.expander("Algorithms"):
            st.markdown(
                """
            ### Implemented Algorithms
            
            **MOCUS** (Method of Obtaining Cut Sets): A systematic procedure for determining minimal cut sets from a fault tree or reliability block diagram.
            
            **Binary Decision Diagrams** (BDD): A data structure that represents Boolean functions efficiently and can be used to find minimal cut sets.
            
            **Inclusion-Exclusion Principle**: A counting technique used to calculate the probability of the union of multiple events (used for exact unreliability calculation).
            """
            )

        with st.expander("References"):
            st.markdown(
                """
            ### References
            
            1. Rausand, M., & Høyland, A. (2004). System reliability theory: models, statistical methods, and applications (Vol. 396). John Wiley & Sons.
            
            2. Kuo, W., & Zuo, M. J. (2003). Optimal reliability modeling: principles and applications. John Wiley & Sons.
            
            3. Modarres, M., Kaminskiy, M. P., & Krivtsov, V. (2016). Reliability engineering and risk analysis: a practical guide. CRC press.
            """
            )
