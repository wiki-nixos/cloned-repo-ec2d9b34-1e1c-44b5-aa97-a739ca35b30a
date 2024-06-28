{self, ...}@inputs:

let
  systemSettings = {
    hostname = "inspiron-laptop"; # hostname, unique identifier for building the flake
    timezone = "Europe/Vienna"; # timezone
    defaultLocale = "en_US.UTF-8"; # default locale
    extraLocale = "de_AT.UTF-8"; # extra locale (for measurement, numeric, time, ...)
    kblayout = "de"; # keyboard layout
    user1 = {
      username = userSettings1.username; # username
      name = userSettings1.name;
    };
  };

  userSettings1 = rec {
    username = "leon"; # username
    name = "Leon"; # name/identifier (used for certain configurations i.e. git)
    email = "leon.erd@student.uibk.ac.at"; # email (used for certain configurations i.e. git)
    flakeDirectory = "/home/${username}/Nextcloud/dotfiles";
    kblayout = "de";
    systemConfigurationName = systemSettings.hostname;
    userConfigurationName = "${username}@${systemConfigurationName}";
  };

  pkgs = import inputs.nixpkgs {
    overlays = [
      inputs.nur.overlay
    ];
    system = "x86_64-linux"; # system arch (checkout hardware-configuration.nix -> nixpkgs.hostPlatform);
    config.allowUnfree = true;
  };

  #pkgsLocal = import inputs.nixpkgsLocal {
  #  system = "x86_64-linux"; # system arch (checkout hardware-configuration.nix -> nixpkgs.hostPlatform);
  #  config.allowUnfree = true;
  #};
in

{
  ${systemSettings.hostname} = inputs.nixpkgs.lib.nixosSystem {
    system = pkgs.system;
    modules = [ ./configuration.nix ];
    specialArgs = {
      inherit pkgs;
      inherit inputs;
      inherit systemSettings;
    };
  };

  ${userSettings1.userConfigurationName} = inputs.home-manager.lib.homeManagerConfiguration {
    inherit pkgs;
    modules = [ ./home.nix ];
    extraSpecialArgs = {
      # pass config variables from above
      inherit inputs;
      userSettings = userSettings1;
      #inherit pkgsLocal;
    };
  };
}
