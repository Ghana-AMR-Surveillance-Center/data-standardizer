# GLASS Data Standardizer - Repository Analysis & Cleanup Report

**Date**: 2025-09-28  
**Analyzer**: Repository Cleanup Bot  
**Repository Path**: `C:\Users\MAdu\OneDrive - The Aurum Institute NPC\Desktop\data-standardizer`

---

## Executive Summary

This report provides a comprehensive analysis of the GLASS Data Standardizer Streamlit application repository. The application is a **data processing and standardization platform** with **AMR (Antimicrobial Resistance) analytics capabilities**. 

**Overall Assessment**: The repository is functional but requires significant cleanup, security hardening, and organization improvements. The codebase is well-structured with clear separation of concerns, but lacks testing infrastructure, has security vulnerabilities (hardcoded secrets), and contains organizational issues.

**Key Findings**:
- ✅ **Functional**: Application runs and appears to work correctly
- ⚠️ **Security**: Hardcoded secrets found in deployment scripts
- ❌ **Testing**: No test suite found
- ⚠️ **Organization**: Multiple duplicate documentation files, large data files in repo
- ⚠️ **CI/CD**: No GitHub Actions or CI configuration found

---

## 1. Repository Structure & File Tree

### Current Structure
```
data-standardizer/
├── app.py                    # Main Streamlit entry point (28 KB)
├── run.py                    # Production launcher (2.3 KB)
├── run_production.py         # Enhanced production launcher (5.5 KB)
├── requirements.txt          # Dependencies (0.5 KB)
├── config.json               # App configuration (1 KB)
├── app_settings.json         # User settings (1.2 KB)
├── Dockerfile                # Container config (1.1 KB)
├── docker-compose.yml        # Multi-container setup (1.4 KB)
├── launch.bat                # Windows dev launcher (1 KB)
├── deploy_production.bat     # Production deployment script (2.4 KB)
├── deploy_production.sh      # Production deployment script (2.2 KB)
├── verify_production.py      # Production verification (5 KB)
│
├── config/
│   ├── production.py         # Production config class (6.6 KB)
│   └── production.env        # Environment template (1.1 KB)
│
├── utils/                    # 25 utility modules (~400 KB total)
│   ├── __init__.py
│   ├── file_handler.py
│   ├── file_merger.py        # Largest file (70 KB)
│   ├── amr_analytics.py      # 38 KB
│   ├── enhanced_amr_analytics.py  # 33 KB
│   ├── amr_interface.py      # 33 KB
│   ├── enhanced_amr_interface.py  # 28 KB
│   ├── transformer.py        # 28 KB
│   ├── column_mapper.py      # 17 KB
│   └── [20 more modules...]
│
├── data/
│   └── PrimaryFile.xlsx      # Sample data (251 KB) ⚠️ Should be gitignored
│
├── logs/                     # Application logs
│   ├── app.log               # 12 KB
│   ├── app_20250928.log
│   ├── errors.log
│   └── security.log
│
├── deployment/               # Deployment docs
│   └── README.md
│
├── scripts/                  # Deployment scripts
│   ├── deploy.bat
│   └── deploy.sh
│
└── venv/                     # Virtual environment ⚠️ Should be gitignored
```

### Documentation Files (Too Many at Root)
- `README.md` (7.7 KB)
- `README_PRODUCTION.md` (8.5 KB)
- `PRODUCTION_SUMMARY.md` (11 KB)
- `PRODUCTION_READY_SUMMARY.md` (7 KB)
- `PRODUCTION_READINESS_SUMMARY.md` (4.6 KB)
- `PRODUCTION_CLEANUP_SUMMARY.md` (6.3 KB)
- `PRODUCTION_GUIDE.md` (9 KB)
- `BUG_FIXES_SUMMARY.md` (5.8 KB)

**Issue**: 8 documentation files at root - should be consolidated into `docs/` folder.

---

## 2. Python Version & Packaging

### Python Version
- **Documented**: Python 3.8+ (README.md)
- **Dockerfile**: Python 3.11-slim
- **Runtime**: No `.python-version` or `runtime.txt` file found
- **Recommendation**: Add `.python-version` file and standardize on Python 3.10 or 3.11

### Packaging Method
- **Primary**: `requirements.txt` (no version pinning, uses `>=`)
- **No**: `pyproject.toml`, `setup.py`, `Pipfile`, or `setup.cfg`
- **Issue**: Dependencies are not pinned, which can cause reproducibility issues

### Entry Points
1. **Main App**: `app.py` (Streamlit app)
2. **Launchers**: 
   - `run.py` - Simple production launcher
   - `run_production.py` - Enhanced production launcher with monitoring
   - `launch.bat` - Windows development launcher

**Command to Run**:
```bash
streamlit run app.py --server.port 8501
# OR
python run.py
# OR  
python run_production.py
```

---

## 3. Dependencies Analysis

### Installed Dependencies (from requirements.txt)

**Core**:
- `streamlit>=1.28.0` - Web framework
- `pandas>=1.5.0` - Data manipulation
- `numpy>=1.21.0` - Numerical computing

**File Processing**:
- `openpyxl>=3.0.9` - Excel file handling
- `xlsxwriter>=3.0.0` - Excel writing
- `xlrd>=2.0.0,<3.0.0` - Legacy Excel support

**Visualization**:
- `plotly>=5.8.0` - Interactive charts
- `kaleido>=0.2.1` - Static image export
- `seaborn>=0.11.0` - Statistical visualizations
- `matplotlib>=3.5.0` - Plotting

**Text Processing**:
- `python-Levenshtein>=0.21.0` - String similarity

**System**:
- `psutil>=5.9.0` - System monitoring
- `scipy>=1.9.0` - Scientific computing

### Issues
1. **No version pinning**: All dependencies use `>=`, which can cause breakage
2. **No security audit**: No evidence of dependency vulnerability scanning
3. **Missing dev dependencies**: No testing tools (pytest, black, ruff, mypy)

---

## 4. Module Dependency Map

### Core Application Flow
```
app.py
├── utils/file_handler.py
├── utils/schema_analyzer.py
├── utils/column_mapper.py
│   └── utils/schema_analyzer.py
├── utils/transformer.py
├── utils/validator.py
├── utils/excel_exporter.py
├── utils/file_merger.py
├── utils/data_quality.py
├── utils/data_profiler.py
├── utils/amr_interface.py
│   ├── utils/amr_analytics.py
│   └── utils/ast_detector.py
├── utils/enhanced_amr_interface.py
│   ├── utils/enhanced_amr_analytics.py
│   └── utils/user_feedback.py
├── utils/logger.py
├── utils/app_config.py
├── utils/user_feedback.py
├── utils/app_settings.py
├── utils/cache_manager.py
├── utils/production_logger.py
└── config/production.py
```

### Utility Module Dependencies
- **amr_analytics.py** → ast_detector.py, cache_manager.py
- **amr_interface.py** → amr_analytics.py, ast_detector.py
- **enhanced_amr_analytics.py** → cache_manager.py
- **enhanced_amr_interface.py** → enhanced_amr_analytics.py, user_feedback.py
- **age_transformer.py** → helpers.py
- **column_mapper.py** → schema_analyzer.py
- **file_merger.py** → (self-contained, large file)

### Circular Dependencies
- **None detected** - Clean dependency structure

### Code Duplication Issues

1. **`detect_date_format()`** - Defined **twice** in `utils/helpers.py` (lines 96 and 247)
2. **Column name cleaning** - Similar implementations in:
   - `utils/helpers.py` → `clean_column_name()`
   - `utils/file_merger.py` → `_clean_column_name_cached()`
   - `utils/column_mapper.py` → Similar logic in `_calculate_similarity()`
3. **Similarity calculations** - Multiple implementations:
   - `utils/column_mapper.py` → `_calculate_similarity()` (uses Levenshtein)
   - `utils/file_merger.py` → `_calculate_name_similarity_fast()` (uses SequenceMatcher)

---

## 5. Security Audit

### 🔴 CRITICAL: Hardcoded Secrets Found

1. **`launch.bat` (line 14)**:
   ```batch
   set SECRET_KEY=dev-secret-key-12345
   ```
   **Risk**: High - Development secret exposed in version control

2. **`deploy_production.bat` (line 61)**:
   ```batch
   set "SECRET_KEY=glass-prod-secret-key-2024"
   ```
   **Risk**: Critical - Production secret exposed in version control

3. **`deploy_production.sh` (line 55)**:
   ```bash
   export SECRET_KEY="glass-prod-secret-key-2024"
   ```
   **Risk**: Critical - Production secret exposed in version control

4. **`config/production.env` (line 11)**:
   ```env
   SECRET_KEY=your-secret-key-here-change-in-production
   ```
   **Risk**: Medium - Template file with placeholder (acceptable, but should be in .gitignore)

5. **Multiple documentation files** mention SECRET_KEY examples:
   - `PRODUCTION_READY_SUMMARY.md`
   - `README_PRODUCTION.md`
   - `PRODUCTION_GUIDE.md`
   - `PRODUCTION_SUMMARY.md`

### Security Recommendations

1. **Immediate Actions**:
   - Remove hardcoded secrets from all files
   - Rotate all exposed secrets immediately
   - Add `.env` files to `.gitignore` (already done)
   - Use environment variables or secret management

2. **Git History Cleanup**:
   - If secrets were committed, consider using `git-filter-repo` or `BFG Repo-Cleaner` to remove them from history
   - Force push to main after cleanup (coordinate with team)

3. **Best Practices**:
   - Never commit secrets to version control
   - Use `.env.example` for templates
   - Use secret management services (AWS Secrets Manager, HashiCorp Vault, etc.) in production

### .gitignore Coverage
✅ **Good**: Covers common patterns:
- `__pycache__/`, `*.pyc`
- `.venv/`, `venv/`
- `*.log`, `logs/`
- `.env`
- `data/*.xlsx`, `data/*.csv`
- IDE files (`.vscode/`, `.idea/`)

⚠️ **Issues**:
- `venv/` folder is in repo (should be removed)
- `logs/` folder has committed log files
- `data/PrimaryFile.xlsx` is committed (251 KB)

---

## 6. Testing & CI/CD

### Test Suite
❌ **No test suite found**
- No `test_*.py` files
- No `tests/` directory
- No `pytest.ini` or `unittest` configuration
- No test coverage configuration

### CI/CD Configuration
❌ **No CI/CD found**
- No `.github/workflows/` directory
- No GitHub Actions workflows
- No Travis CI, CircleCI, or other CI configs
- No pre-commit hooks configuration

### Recommendations
1. **High Priority**: Add unit tests for critical logic (file handling, data transformation, AMR analytics)
2. **High Priority**: Add integration tests for UI workflows
3. **Medium Priority**: Set up GitHub Actions for:
   - Linting (black, ruff)
   - Type checking (mypy)
   - Running tests
   - Docker image building
4. **Medium Priority**: Add pre-commit hooks for code quality

---

## 7. Code Quality Analysis

### Type Hints
✅ **Good**: Most modules use type hints
- Files use `typing` module (Dict, List, Optional, Tuple, etc.)
- Function signatures include type annotations

### Docstrings
✅ **Good**: Most modules have docstrings
- Module-level docstrings present
- Class and function docstrings present
- Some functions lack detailed docstrings

### Code Style
⚠️ **No enforcement**:
- No `black` or `autopep8` configuration
- No `ruff` or `flake8` configuration
- No `.editorconfig`
- Code style appears consistent but not enforced

### Issues Found

1. **Duplicate Function** (CRITICAL):
   - `detect_date_format()` defined twice in `utils/helpers.py`
   - Line 96 and Line 247
   - **Action Required**: Remove duplicate

2. **Inconsistent Error Handling**:
   - Some modules have comprehensive try-except blocks
   - Others rely on Streamlit's error handling
   - **Recommendation**: Standardize error handling approach

3. **Large Files**:
   - `utils/file_merger.py` - 70 KB (1251 lines)
   - **Recommendation**: Consider splitting into smaller modules

4. **Streamlit Best Practices**:
   - ✅ Uses `st.cache_data` / `st.cache_resource` (via cache_manager)
   - ✅ Uses session state appropriately
   - ⚠️ Some heavy computation could benefit from caching

---

## 8. Behavior vs. Expected Intent

### Implemented Features (from code analysis)

1. **Single File Workflow** ✅
   - Upload → Map → Transform → Validate → Export
   - Status: Fully implemented

2. **Multiple File Merging** ✅
   - Upload → Merge → Transform → Validate → Export
   - Status: Fully implemented with intelligent column mapping

3. **AMR Analytics** ✅
   - Standard AMR interface
   - Enhanced AMR interface with statistical analysis
   - CLSI compliance
   - Status: Fully implemented

4. **Data Quality Assessment** ✅
   - Completeness, consistency, accuracy, validity, uniqueness
   - Status: Fully implemented

5. **Export Functionality** ✅
   - CSV, Excel, JSON, XML formats
   - Status: Fully implemented

### Potential Issues

1. **AMR Interface Duplication**:
   - Both `amr_interface.py` and `enhanced_amr_interface.py` exist
   - User can toggle between them in sidebar
   - **Question**: Is this intentional or should they be merged?

2. **Configuration Files**:
   - `config.json` - App configuration
   - `app_settings.json` - User settings
   - `config/production.py` - Production config class
   - `config/production.env` - Environment template
   - **Potential confusion**: Multiple config sources

3. **Launcher Scripts**:
   - `run.py` - Simple launcher
   - `run_production.py` - Enhanced launcher
   - `launch.bat` - Dev launcher
   - **Question**: Which should users use?

---

## 9. Prioritized Cleanup Plan

### Priority 1: CRITICAL (Security & Functionality)

#### 1.1 Remove Hardcoded Secrets ⚠️ **CRITICAL**
- **Risk**: High - Security breach risk
- **Files**: `launch.bat`, `deploy_production.bat`, `deploy_production.sh`
- **Action**: 
  - Remove hardcoded SECRET_KEY values
  - Use environment variables or secret management
  - Rotate exposed secrets
- **Verification**: Grep for "SECRET_KEY" and verify no hardcoded values
- **Time**: 30 minutes

#### 1.2 Fix Duplicate Function
- **Risk**: Medium - Potential bugs
- **File**: `utils/helpers.py`
- **Action**: Remove duplicate `detect_date_format()` function (keep one implementation)
- **Verification**: Run `grep -n "def detect_date_format" utils/helpers.py` - should show only one match
- **Time**: 15 minutes

#### 1.3 Remove venv from Repository
- **Risk**: Low - Repository bloat
- **Action**: 
  - Add `venv/` to `.gitignore` (already present)
  - Remove `venv/` from git tracking: `git rm -r --cached venv/`
- **Verification**: `git status` should not show venv/
- **Time**: 5 minutes

### Priority 2: HIGH (Code Quality & Organization)

#### 2.1 Consolidate Documentation
- **Risk**: Low - User confusion
- **Action**: 
  - Create `docs/` directory
  - Move all `*_SUMMARY.md`, `*_GUIDE.md`, `README_PRODUCTION.md` to `docs/`
  - Keep only `README.md` at root
  - Create `docs/INDEX.md` with navigation
- **Verification**: Root should have only `README.md`
- **Time**: 30 minutes

#### 2.2 Pin Dependency Versions
- **Risk**: Medium - Reproducibility issues
- **File**: `requirements.txt`
- **Action**: 
  - Generate `requirements.txt` with pinned versions: `pip freeze > requirements.txt`
  - Create `requirements-dev.txt` for development dependencies
  - Consider using `pip-tools` for dependency management
- **Verification**: All dependencies should have `==` versions
- **Time**: 30 minutes

#### 2.3 Remove Large Data Files from Git
- **Risk**: Low - Repository bloat
- **File**: `data/PrimaryFile.xlsx` (251 KB)
- **Action**: 
  - Move to `.gitignore` (already covered)
  - Remove from git: `git rm --cached data/PrimaryFile.xlsx`
  - Add `data/.gitkeep` to preserve directory structure
  - Document in README that sample data should be downloaded separately
- **Verification**: `git ls-files data/` should not show .xlsx files
- **Time**: 10 minutes

#### 2.4 Add .python-version File
- **Risk**: Low - Environment consistency
- **Action**: Create `.python-version` with `3.10` or `3.11`
- **Verification**: File exists with correct version
- **Time**: 2 minutes

### Priority 3: MEDIUM (Testing & CI/CD)

#### 3.1 Create Test Structure
- **Risk**: Medium - Quality assurance
- **Action**: 
  - Create `tests/` directory
  - Add `tests/__init__.py`
  - Create `tests/unit/` and `tests/integration/` subdirectories
  - Add `pytest.ini` configuration
  - Create initial test for critical functions (e.g., file_handler, transformer)
- **Verification**: Run `pytest` - should discover tests
- **Time**: 2 hours

#### 3.2 Add GitHub Actions Workflow
- **Risk**: Low - CI/CD automation
- **Action**: 
  - Create `.github/workflows/ci.yml`
  - Add jobs for: linting, type checking, testing, Docker build
- **Verification**: Push to GitHub, verify workflow runs
- **Time**: 1 hour

#### 3.3 Add Pre-commit Hooks
- **Risk**: Low - Code quality
- **Action**: 
  - Create `.pre-commit-config.yaml`
  - Add hooks for: black, ruff, mypy, trailing whitespace
  - Add `pre-commit install` to setup instructions
- **Verification**: Run `pre-commit run --all-files`
- **Time**: 30 minutes

#### 3.4 Add Code Formatting Configuration
- **Risk**: Low - Code consistency
- **Action**: 
  - Create `pyproject.toml` with black, ruff, mypy configuration
  - Format all code: `black .` and `ruff check --fix .`
- **Verification**: Run `black --check .` - should pass
- **Time**: 30 minutes

### Priority 4: LOW (Organization & Polish)

#### 4.1 Consolidate Similar Functions
- **Risk**: Low - Code maintainability
- **Action**: 
  - Create shared utility for column name cleaning
  - Refactor `file_merger.py` and `column_mapper.py` to use shared utility
- **Verification**: Only one implementation of column cleaning exists
- **Time**: 1 hour

#### 4.2 Split Large Files
- **Risk**: Low - Code maintainability
- **File**: `utils/file_merger.py` (70 KB, 1251 lines)
- **Action**: Consider splitting into:
  - `file_merger.py` - Main merger class
  - `file_merger_utils.py` - Utility functions
  - `similarity_calculator.py` - Similarity logic
- **Verification**: No single file > 1000 lines
- **Time**: 2 hours

#### 4.3 Add Type Checking Configuration
- **Risk**: Low - Code quality
- **Action**: 
  - Create `mypy.ini` configuration
  - Add type checking to CI
  - Fix type errors gradually
- **Verification**: Run `mypy .` - should pass or show acceptable errors
- **Time**: 1 hour

---

## 10. Proposed Target Repository Structure

```
data-standardizer/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI
├── .pre-commit-config.yaml           # Pre-commit hooks
├── .python-version                   # Python version (3.10 or 3.11)
├── .gitignore                        # Git ignore rules
├── pyproject.toml                    # Project configuration (black, ruff, mypy)
├── requirements.txt                  # Pinned production dependencies
├── requirements-dev.txt              # Development dependencies
├── pytest.ini                        # Pytest configuration
├── Dockerfile                        # Container definition
├── docker-compose.yml                # Multi-container setup
│
├── README.md                         # Main documentation (only one at root)
├── CONTRIBUTING.md                   # Contribution guidelines
├── LICENSE                           # License file
│
├── docs/                             # All documentation
│   ├── INDEX.md                      # Documentation index
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── PRODUCTION.md                 # Production guide
│   ├── DEVELOPMENT.md                # Development guide
│   └── API.md                        # API documentation (if needed)
│
├── src/                              # Source code (optional reorganization)
│   └── glass_data_standardizer/      # Package name
│       ├── __init__.py
│       ├── app.py                    # Main Streamlit app
│       ├── config/                   # Configuration
│       │   ├── __init__.py
│       │   └── production.py
│       └── utils/                    # Utility modules
│           ├── __init__.py
│           ├── file_handler.py
│           ├── file_merger.py
│           └── [other modules...]
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   ├── unit/                         # Unit tests
│   │   ├── __init__.py
│   │   ├── test_file_handler.py
│   │   ├── test_transformer.py
│   │   └── ...
│   └── integration/                  # Integration tests
│       ├── __init__.py
│       ├── test_workflows.py
│       └── ...
│
├── scripts/                          # Utility scripts
│   ├── deploy.sh
│   ├── deploy.bat
│   └── setup.sh
│
├── data/                             # Data directory (gitignored)
│   └── .gitkeep
│
├── logs/                             # Logs (gitignored)
│   └── .gitkeep
│
└── config/                           # Configuration files (templates)
    ├── production.env.example        # Template (not actual secrets)
    └── .env.example                  # Development template
```

### Migration Notes

**Current → Proposed Mapping**:
- `app.py` → `src/glass_data_standardizer/app.py` (or keep at root)
- `utils/` → `src/glass_data_standardizer/utils/` (or keep at root)
- `config/` → Keep at root (or move to `src/`)
- All `*_SUMMARY.md`, `*_GUIDE.md` → `docs/`
- `README_PRODUCTION.md` → `docs/PRODUCTION.md`

**Recommendation**: Start with **minimal reorganization** (just docs), then gradually move to `src/` structure if needed.

---

## 11. Commands & Verification Steps

### Installation & Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running the Application
```bash
# Simple run
streamlit run app.py --server.port 8501

# Production launcher
python run_production.py

# Direct Streamlit
python -m streamlit run app.py
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_file_handler.py
```

### Code Quality Checks
```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy .

# Run all checks
pre-commit run --all-files
```

### Security Checks
```bash
# Check for secrets (grep)
grep -r "SECRET_KEY" . --exclude-dir=venv --exclude-dir=.git

# Check dependencies for vulnerabilities
pip install safety
safety check

# Or use pip-audit (newer)
pip install pip-audit
pip-audit
```

---

## 12. Follow-up Questions for Repository Owner

1. **Secrets & Security**:
   - Have the hardcoded secrets in deployment scripts been rotated?
   - Should we use a secret management service (AWS Secrets Manager, etc.)?
   - Do you want to clean Git history to remove committed secrets?

2. **Testing**:
   - What is the expected test coverage target?
   - Are there specific workflows that need integration testing?
   - Should we prioritize unit tests for specific modules?

3. **CI/CD**:
   - Do you have a preferred CI/CD platform (GitHub Actions, GitLab CI, etc.)?
   - Should we set up automated Docker image builds?
   - Do you want deployment automation?

4. **Repository Structure**:
   - Do you prefer keeping `app.py` at root or moving to `src/` structure?
   - Should we consolidate all documentation into `docs/`?
   - Do you want to maintain backward compatibility with existing deployment scripts?

5. **Dependencies**:
   - Should we pin all dependency versions for reproducibility?
   - Are there specific Python versions you need to support?
   - Do you want to add dependency vulnerability scanning to CI?

6. **Features**:
   - Are both AMR interfaces (standard and enhanced) needed, or should they be merged?
   - Which launcher script should be the "official" one?
   - Are there any planned features that affect the cleanup plan?

---

## 13. Next Steps

1. **Immediate** (Today):
   - Remove hardcoded secrets from deployment scripts
   - Fix duplicate `detect_date_format()` function
   - Remove `venv/` from git tracking

2. **Short-term** (This Week):
   - Consolidate documentation into `docs/`
   - Pin dependency versions
   - Remove large data files from git
   - Add `.python-version` file

3. **Medium-term** (This Month):
   - Create test structure and add initial tests
   - Set up GitHub Actions CI workflow
   - Add pre-commit hooks
   - Add code formatting configuration

4. **Long-term** (Next Quarter):
   - Consolidate duplicate functions
   - Split large files if needed
   - Add comprehensive test coverage
   - Optimize Docker image

---

## Appendix A: File Sizes Summary

| File | Size (KB) | Notes |
|------|-----------|-------|
| `data/PrimaryFile.xlsx` | 251 | ⚠️ Should be gitignored |
| `utils/file_merger.py` | 70 | ⚠️ Very large, consider splitting |
| `utils/amr_analytics.py` | 38 | - |
| `utils/enhanced_amr_analytics.py` | 33 | - |
| `utils/amr_interface.py` | 33 | - |
| `utils/enhanced_amr_interface.py` | 28 | - |
| `app.py` | 28 | Main entry point |
| `utils/transformer.py` | 28 | - |
| `logs/app.log` | 12 | ⚠️ Should be gitignored |
| `PRODUCTION_GUIDE.md` | 9 | Should move to docs/ |

---

## Appendix B: Module Dependency Graph (Text)

```
app.py
├── config.production
├── utils.file_handler
├── utils.schema_analyzer
├── utils.column_mapper → utils.schema_analyzer
├── utils.transformer
├── utils.validator
├── utils.excel_exporter
├── utils.file_merger
├── utils.data_quality
├── utils.data_profiler
├── utils.amr_interface
│   ├── utils.amr_analytics → utils.ast_detector, utils.cache_manager
│   └── utils.ast_detector
├── utils.enhanced_amr_interface
│   ├── utils.enhanced_amr_analytics → utils.cache_manager
│   └── utils.user_feedback
├── utils.logger
├── utils.app_config
├── utils.user_feedback
├── utils.app_settings
├── utils.cache_manager
└── utils.production_logger
```

---

**Report Generated**: 2025-09-28  
**Next Review**: After cleanup implementation

