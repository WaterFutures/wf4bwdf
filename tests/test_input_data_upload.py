import pytest
import pandas as pd

from pathlib import Path
from wf4bwdf import load_complete_dataset, load_iteration_dataset
from wf4bwdf._data_loading import N_EVAL_WEEKS

class TestDataLoading:
    """Test data loading functions and save all outputs to Excel"""
    
    @pytest.fixture(scope="class")
    def output_dir(self):
        """Create output directory for Excel files"""
        output_path = Path("test_outputs")
        output_path.mkdir(exist_ok=True)
        return output_path
    
    def test_load_complete_dataset_all_combinations(self, output_dir):
        """Test load_complete_dataset with all parameter combinations"""
        
        test_cases = [
            {"use_letters_for_names": True},
            {"use_letters_for_names": False}
        ]
        
        for i, params in enumerate(test_cases):
            # Load the dataset
            dataset = load_complete_dataset(**params)
            
            # Basic structure assertions
            assert isinstance(dataset, dict), f"Dataset should be dict for case {i}"
            expected_keys = ['dma-properties', 'dma-inflows', 'weather', 'calendar']
            
            # Check all expected keys exist
            for key in expected_keys:
                assert any(expected_key in dataset for expected_key in expected_keys), f"Missing expected keys for case {i}"
            
            # Check all values are DataFrames
            for key, df in dataset.items():
                assert isinstance(df, pd.DataFrame), f"{key} should be DataFrame for case {i}"
                assert not df.empty, f"{key} should not be empty for case {i}"
            
            # Save to Excel
            filename = f"complete_dataset_letters_{params['use_letters_for_names']}.xlsx"
            filepath = output_dir / filename
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for key, df in dataset.items():
                    # Clean sheet name (Excel has 31 char limit and no special chars)
                    if hasattr(df.index, 'tz'):
                        df.index = df.index.tz_localize(None)
                    sheet_name = key.replace('_', '')[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=True)
            
            print(f"✓ Saved complete dataset (letters={params['use_letters_for_names']}) to {filepath}")
    
    def test_load_iteration_dataset_all_combinations(self, output_dir):
        """Test load_iteration_dataset with all parameter combinations"""
        
        # Test iterations: first, middle, last, and a few random ones
        test_iterations = list(range(1,5))
        
        use_letters_options = [True, False]
        
        for iteration in test_iterations:
            for use_letters in use_letters_options:
                # Load the dataset
                dataset = load_iteration_dataset(
                    iteration=iteration, 
                    use_letters_for_names=use_letters
                )
                
                # Basic structure assertions
                assert isinstance(dataset, dict), f"Dataset should be dict for iteration {iteration}, letters {use_letters}"
                
                # Check all values are DataFrames
                for key, df in dataset.items():
                    assert isinstance(df, pd.DataFrame), f"{key} should be DataFrame for iteration {iteration}"
                
                # Save to Excel
                filename = f"iteration_dataset_iter_{iteration}_letters_{use_letters}.xlsx"
                filepath = output_dir / filename
                
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    for key, df in dataset.items():
                        if hasattr(df.index, 'tz'):
                            df.index = df.index.tz_localize(None)
                        sheet_name = key.replace('_', '')[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=True)
                
                print(f"✓ Saved iteration dataset (iter={iteration}, letters={use_letters}) to {filepath}")
    
    def test_invalid_inputs(self):
        """Test that invalid inputs raise appropriate errors"""
        
        # Test invalid iteration values ok between 1 and 4
        with pytest.raises(ValueError):
            load_iteration_dataset(iteration=0)
        
        with pytest.raises(ValueError):
            load_iteration_dataset(iteration=5)
        
        # Make sure float are not allowed, for the rest fo the types doesn't really matter
        with pytest.raises(ValueError):
            load_iteration_dataset(iteration=1.5)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])